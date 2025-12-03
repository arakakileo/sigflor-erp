from django.db.models import QuerySet, Q, Count, Sum
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from ..models import Contrato, Usuario, Filial # Adicione Filial para o filtro de permissão

def contrato_list(
    *,
    user: Usuario, # Adicionado parametro user
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    vigente: bool = None,
    cliente_id: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista contratos com filtros opcionais, respeitando permissoes regionais do usuario."""
    qs = Contrato.objects.filter(
        deleted_at__isnull=True
    ).select_related('cliente', 'empresa', 'cliente__pessoa_juridica', 'empresa__pessoa_juridica')

    if not user.is_superuser:
        # Contratos são associados a Empresas e Clientes, que podem estar em Filiais.
        # Para o MVP, assumimos que a permissão é pela filial associada à empresa do contrato
        # ou que o contrato em si não tem restrição regional direta, mas é acessível se as filiais do usuário
        # estão em alguma Empresa que gerencia o cliente do contrato.
        # Esta é uma lógica que pode ser refinada, mas para o MVP, vamos considerar a empresa do contrato.
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if vigente is True:
        hoje = timezone.now().date()
        qs = qs.filter(
            ativo=True,
            data_inicio__lte=hoje
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
        )
    elif vigente is False:
        hoje = timezone.now().date()
        qs = qs.filter(
            Q(ativo=False) |
            Q(data_inicio__gt=hoje) |
            Q(data_fim__lt=hoje)
        )

    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(numero_interno__icontains=search) |
            Q(numero_externo__icontains=search) |
            Q(cliente__pessoa_juridica__razao_social__icontains=search)
        )

    return qs.order_by('-data_inicio', 'numero_interno')


def contrato_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Contrato:
    """Obtem detalhes de um contrato com relacionamentos, verificando permissao regional."""
    contrato = Contrato.objects.select_related(
        'cliente', 'empresa',
        'cliente__pessoa_juridica', 'empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id__in=contrato.empresa.filiais.all()).exists():
             raise PermissionDenied(f"Usuário não tem acesso ao contrato {contrato.numero_interno} via filial.")

    return contrato


def contratos_vigentes(
    *,
    user: Usuario, # Adicionado parametro user
    cliente_id: str = None, empresa_id: str = None
) -> QuerySet:
    """Lista contratos vigentes, respeitando permissoes regionais do usuario."""
    hoje = timezone.now().date()
    qs = Contrato.objects.filter(
        ativo=True,
        data_inicio__lte=hoje,
        deleted_at__isnull=True
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).select_related('cliente', 'empresa')

    if not user.is_superuser:
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('-data_inicio', 'numero_interno')


def estatisticas_contratos(*, user: Usuario) -> dict:
    """Retorna estatisticas de contratos, respeitando permissoes regionais do usuario."""
    qs = Contrato.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

    hoje = timezone.now().date()

    total = qs.count()
    ativos = qs.filter(ativo=True).count()
    vigentes = qs.filter(
        ativo=True,
        data_inicio__lte=hoje
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).count()

    valor_total = qs.filter(ativo=True).aggregate(
        total=Sum('valor')
    )['total'] or 0

    return {
        'total': total,
        'ativos': ativos,
        'inativos': total - ativos,
        'vigentes': vigentes,
        'valor_total': valor_total,
    }
