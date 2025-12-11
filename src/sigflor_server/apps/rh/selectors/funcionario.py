from django.db.models import QuerySet, Q, Count
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from ..models import Funcionario, enums
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# Funcionário Selectors
# ============================================================================

def funcionario_list(
    *,
    user: Usuario,
    busca: str = None,
    status: str = None,
    tipo_contrato: str = None,
    empresa_id: str = None,
    cargo_id: str = None,
    projeto_id: str = None,
    apenas_ativos: bool = False
) -> QuerySet:

    qs = Funcionario.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'projeto',
        'projeto__filial',
    )

    # # Filtro Regional (RBAC por Filial)
    # if not user.is_superuser:
    #     # O funcionário pertence a um projeto, que pertence a uma filial.
    #     # Se o funcionário não tiver projeto, ele pode ficar "invisível" ou visível apenas para admin.
    #     # Aqui assumimos que se tiver projeto, filtramos. Se não, permitimos (ou bloqueamos).
    #     # Regra segura: Só mostra se estiver em projeto de filial permitida OU se não tiver projeto (staged).
    #     qs = qs.filter(
    #         Q(projeto__filial__in=user.allowed_filiais.all()) |
    #         Q(projeto__isnull=True)
    #     ).distinct()

    if apenas_ativos:
        qs = qs.filter(status=enums.StatusFuncionario.ATIVO)

    if status:
        qs = qs.filter(status=status)

    if tipo_contrato:
        qs = qs.filter(tipo_contrato=tipo_contrato)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if cargo_id:
        qs = qs.filter(cargo_id=cargo_id)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    if busca:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=busca) |
            Q(pessoa_fisica__cpf__icontains=busca) |
            Q(matricula__icontains=busca) |
            Q(cargo__nome__icontains=busca)
        )

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionario_detail(*, user: Usuario, pk) -> Funcionario:
    """Obtém detalhes de um funcionário com relacionamentos otimizados."""
    # Nota: Usamos os nomes das relações reversas (related_name) definidos nos models do Core
    funcionario = Funcionario.objects.select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'projeto',
        'projeto__filial',
    ).prefetch_related(
        # Correção dos caminhos de prefetch para usar as tabelas de vínculo corretas
        'pessoa_fisica__enderecos_vinculados__endereco',
        'pessoa_fisica__contatos_vinculados__contato',
        'pessoa_fisica__documentos_vinculados__documento',
        'dependentes',
        'dependentes__pessoa_fisica',
        'alocacoes',
        'alocacoes__projeto',
        'alocacoes_equipe',
        'alocacoes_equipe__equipe'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser and funcionario.projeto:
        if not user.allowed_filiais.filter(id=funcionario.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso à filial deste funcionário.")

    return funcionario


def funcionarios_por_empresa(*, user: Usuario, empresa_id: str) -> QuerySet:
    """Lista funcionários de uma empresa específica."""
    qs = Funcionario.objects.filter(
        empresa_id=empresa_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_projeto(*, user: Usuario, projeto_id: str) -> QuerySet:
    """Lista funcionários de um projeto específico."""
    qs = Funcionario.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        # Verifica se o usuário tem acesso à filial do projeto solicitado
        # Como estamos filtrando por um projeto específico, podemos checar a filial dele indiretamente
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_ativos(*, user: Usuario) -> QuerySet:
    """Lista apenas funcionários ativos."""
    qs = Funcionario.objects.filter(
        status=enums.StatusFuncionario.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_afastados(*, user: Usuario) -> QuerySet:
    """Lista funcionários afastados (afastado, férias)."""
    qs = Funcionario.objects.filter(
        status__in=[enums.StatusFuncionario.AFASTADO, enums.StatusFuncionario.FERIAS],
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_admitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionários admitidos em um período."""
    qs = Funcionario.objects.filter(
        data_admissao__gte=data_inicio,
        data_admissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('-data_admissao')


def funcionarios_demitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionários demitidos em um período."""
    qs = Funcionario.objects.filter(
        data_demissao__gte=data_inicio,
        data_demissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('-data_demissao')


def aniversariantes_mes(*, user: Usuario, mes: int = None) -> QuerySet:
    """Lista funcionários que fazem aniversário no mês."""
    if mes is None:
        mes = timezone.now().month

    qs = Funcionario.objects.filter(
        pessoa_fisica__data_nascimento__month=mes,
        status=enums.StatusFuncionario.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__data_nascimento__day')


def estatisticas_rh(*, user: Usuario) -> dict:
    """Retorna estatísticas gerais do RH."""
    qs = Funcionario.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    total = qs.count()
    ativos = qs.filter(status=enums.StatusFuncionario.ATIVO).count()
    afastados = qs.filter(status__in=[
        enums.StatusFuncionario.AFASTADO,
        enums.StatusFuncionario.FERIAS
    ]).count()

    por_tipo_contrato = qs.filter(
        status=enums.StatusFuncionario.ATIVO
    ).values('tipo_contrato').annotate(
        total=Count('id')
    ).order_by('-total')

    por_cargo = qs.filter(
        status=enums.StatusFuncionario.ATIVO
    ).values('cargo__nome').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    return {
        'total': total,
        'ativos': ativos,
        'afastados': afastados,
        'por_tipo_contrato': list(por_tipo_contrato),
        'por_cargo': list(por_cargo),
    }
