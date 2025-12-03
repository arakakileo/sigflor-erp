from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from ..models import Endereco

def endereco_list_por_entidade(*, entidade, principal: bool = None) -> QuerySet:
    """Lista enderecos de uma entidade. (FIXME: Lógica de GFK pode precisar de revisão)"""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Endereco.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if principal is not None:
        qs = qs.filter(principal=principal)

    return qs.order_by('-principal', '-created_at')
