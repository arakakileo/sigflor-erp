from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from ..models import Alocacao
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# Alocação Selectors
# ============================================================================

def alocacao_list(
    *,
    user: Usuario,
    funcionario_id: str = None,
    projeto_id: str = None,
    apenas_ativas: bool = False
) -> QuerySet:
    """Lista alocações com filtros opcionais."""
    qs = Alocacao.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'projeto',
        'projeto__filial'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativas:
        qs = qs.filter(data_fim__isnull=True)

    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    return qs.order_by('-data_inicio')


def alocacao_detail(*, user: Usuario, pk) -> Alocacao:
    """Obtém detalhes de uma alocação."""
    alocacao = Alocacao.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo',
        'projeto',
        'projeto__filial'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=alocacao.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso a esta alocação.")

    return alocacao


def alocacoes_por_funcionario(*, user: Usuario, funcionario_id: str) -> QuerySet:
    """Lista histórico de alocações de um funcionário."""
    qs = Alocacao.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).select_related('projeto', 'projeto__filial')

    if not user.is_superuser:
        # Mostra apenas alocações que o usuário tem permissão de ver
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_inicio')


def alocacoes_por_projeto(*, user: Usuario, projeto_id: str, apenas_ativas: bool = True) -> QuerySet:
    """Lista alocações de um projeto."""
    qs = Alocacao.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo',
        'projeto__filial'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativas:
        qs = qs.filter(data_fim__isnull=True)

    return qs.order_by('funcionario__pessoa_fisica__nome_completo')
