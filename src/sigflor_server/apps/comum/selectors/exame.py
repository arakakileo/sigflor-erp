from django.db.models import QuerySet, Q
from ..models import Exame

def exame_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista exames com filtros opcionais."""
    qs = Exame.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search)
        )

    return qs.order_by('nome')


def exame_detail(*, pk) -> Exame:
    """Obtem detalhes de um exame."""
    return Exame.objects.get(pk=pk, deleted_at__isnull=True)
