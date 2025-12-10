from django.db.models import QuerySet, Q
from rest_framework.exceptions import PermissionDenied

from ..models import Equipe, EquipeFuncionario
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# Equipe Selectors
# ============================================================================

def equipe_list(
    *,
    user: Usuario,
    busca: str = None,
    projeto_id: str = None,
    tipo_equipe: str = None,
    apenas_ativas: bool = True
) -> QuerySet:
    """Lista equipes com filtros opcionais."""
    qs = Equipe.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'projeto',
        'projeto__filial',
        'lider',
        'lider__pessoa_fisica',
        'coordenador',
        'coordenador__pessoa_fisica'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativas:
        qs = qs.filter(ativa=True)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    if tipo_equipe:
        qs = qs.filter(tipo_equipe=tipo_equipe)

    if busca:
        qs = qs.filter(
            Q(nome__icontains=busca) |
            Q(projeto__descricao__icontains=busca)
        )

    return qs.order_by('nome')


def equipe_detail(*, user: Usuario, pk) -> Equipe:
    """Obtém detalhes de uma equipe."""
    equipe = Equipe.objects.select_related(
        'projeto',
        'projeto__filial',
        'lider',
        'lider__pessoa_fisica',
        'coordenador',
        'coordenador__pessoa_fisica'
    ).prefetch_related(
        'membros',
        'membros__funcionario',
        'membros__funcionario__pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=equipe.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso a esta equipe.")

    return equipe


def equipes_por_projeto(*, user: Usuario, projeto_id: str) -> QuerySet:
    """Lista equipes de um projeto."""
    qs = Equipe.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related(
        'lider__pessoa_fisica',
        'coordenador__pessoa_fisica',
        'projeto__filial'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('nome')


def membros_equipe(*, user: Usuario, equipe_id: str, apenas_ativos: bool = True) -> QuerySet:
    """Lista membros de uma equipe."""
    qs = EquipeFuncionario.objects.filter(
        equipe_id=equipe_id,
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo',
        'equipe__projeto__filial'
    )

    # Validar permissão regional baseada na equipe
    if not user.is_superuser:
        # Se o usuário não tiver acesso à equipe, retorna vazio (ou poderia lançar erro)
        qs = qs.filter(equipe__projeto__filial__in=user.allowed_filiais.all())

    if apenas_ativos:
        qs = qs.filter(data_saida__isnull=True)

    return qs.order_by('funcionario__pessoa_fisica__nome_completo')
