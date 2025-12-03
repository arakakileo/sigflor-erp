from django.db.models import QuerySet, Q
from ..models import Usuario

def usuario_list(*, filters: dict = None, search: str = None, ativo: bool = None) -> QuerySet:
    """Lista usuarios com filtros opcionais."""
    qs = Usuario.objects.filter(deleted_at__isnull=True)

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    return qs.select_related('pessoa_fisica').prefetch_related('papeis').order_by('username')


def usuario_detail(*, pk) -> Usuario:
    """Obtem detalhes de um usuario com relacionamentos."""
    return Usuario.objects.select_related(
        'pessoa_fisica'
    ).prefetch_related(
        'papeis', 'papeis__permissoes', 'permissoes_diretas'
    ).get(pk=pk, deleted_at__isnull=True)
