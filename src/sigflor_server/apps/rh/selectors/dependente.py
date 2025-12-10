from django.db.models import QuerySet, Q, Count
from rest_framework.exceptions import PermissionDenied

from ..models import Funcionario, Dependente
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# Dependente Selectors
# ============================================================================

def dependente_list(
    *,
    user: Usuario,
    funcionario_id: str = None,
    busca: str = None,
    parentesco: str = None,
    dependencia_irrf: bool = None,
    apenas_ativos: bool = True
) -> QuerySet:
    """Lista dependentes com filtros opcionais."""
    qs = Dependente.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__projeto', # Necessário para o filtro regional
        'pessoa_fisica'
    )

    if not user.is_superuser:
        qs = qs.filter(
            Q(funcionario__projeto__filial__in=user.allowed_filiais.all()) |
            Q(funcionario__projeto__isnull=True)
        ).distinct()

    if apenas_ativos:
        qs = qs.filter(ativo=True)

    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)

    if parentesco:
        qs = qs.filter(parentesco=parentesco)

    if dependencia_irrf is not None:
        qs = qs.filter(dependencia_irrf=dependencia_irrf)

    if busca:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=busca) |
            Q(pessoa_fisica__cpf__icontains=busca)
        )

    return qs.order_by('funcionario__pessoa_fisica__nome_completo', 'pessoa_fisica__nome_completo')


def dependente_detail(*, user: Usuario, pk) -> Dependente:
    """Obtém detalhes de um dependente."""
    dependente = Dependente.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__projeto',
        'pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser and dependente.funcionario.projeto:
        if not user.allowed_filiais.filter(
            id=dependente.funcionario.projeto.filial_id
        ).exists():
            raise PermissionDenied("Usuário não tem acesso a este dependente.")

    return dependente


def dependentes_por_funcionario(*, user: Usuario, funcionario_id: str) -> QuerySet:
    """Lista dependentes de um funcionário específico."""
    qs = Dependente.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    # Validação de acesso já implícita se o usuário chegou até aqui via API do funcionário,
    # mas reforçamos por segurança
    if not user.is_superuser:
        qs = qs.filter(
            Q(funcionario__projeto__filial__in=user.allowed_filiais.all()) |
            Q(funcionario__projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_com_dependentes(*, user: Usuario) -> QuerySet:
    """Lista funcionários que possuem dependentes."""
    qs = Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_dependentes(*, user: Usuario) -> dict:
    """Retorna estatísticas de dependentes."""
    qs = Dependente.objects.filter(deleted_at__isnull=True, ativo=True)

    if not user.is_superuser:
        qs = qs.filter(
            Q(funcionario__projeto__filial__in=user.allowed_filiais.all()) |
            Q(funcionario__projeto__isnull=True)
        ).distinct()

    total = qs.count()
    irrf = qs.filter(dependencia_irrf=True).count()

    por_parentesco = qs.values('parentesco').annotate(
        total=Count('id')
    ).order_by('-total')

    funcionarios_qs = Funcionario.objects.filter(tem_dependente=True, deleted_at__isnull=True)
    if not user.is_superuser:
        funcionarios_qs = funcionarios_qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        )
    funcionarios_com_dep = funcionarios_qs.count()

    return {
        'total_dependentes': total,
        'irrf': irrf,
        'por_parentesco': list(por_parentesco),
        'funcionarios_com_dependentes': funcionarios_com_dep,
    }
