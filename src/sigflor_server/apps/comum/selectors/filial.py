from django.db.models import QuerySet, Q, Count
from rest_framework.exceptions import PermissionDenied
from ..models import Filial, Usuario

def filial_list(
    *,
    user: Usuario, # Adicionado parametro user
    filters: dict = None,
    search: str = None,
    status: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista filiais com filtros opcionais, respeitando permissoes regionais do usuario."""
    qs = Filial.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all()) # Filtra por filiais permitidas ao usuario

    qs = qs.select_related('empresa')

    if status:
        qs = qs.filter(status=status)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(codigo_interno__icontains=search)
        )

    return qs.order_by('nome')


def filial_detail(*, user: Usuario, pk) -> Filial:
    """Obtem detalhes de uma filial com relacionamentos, verificando permissao regional."""
    filial = Filial.objects.select_related(
        'empresa', 'empresa__pessoa_juridica'
    ).prefetch_related(
        'enderecos_vinculados__endereco',
        'contatos_vinculados__contato'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
    
    return filial


def filiais_ativas(*, user: Usuario, empresa_id: str = None) -> QuerySet:
    """Lista filiais ativas, respeitando permissoes regionais do usuario."""
    qs = Filial.objects.filter(
        status=Filial.Status.ATIVA,
        deleted_at__isnull=True
    )
    
    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all())

    qs = qs.select_related('empresa')

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('nome')


def estatisticas_filiais(*, user: Usuario) -> dict:
    """Retorna estatisticas de filiais, respeitando permissoes regionais do usuario."""
    qs = Filial.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all())

    total = qs.count()

    por_status = qs.values('status').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total': total,
        'por_status': list(por_status),
    }
