from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from ..models import Anexo

def anexo_list_por_entidade(*, entidade, mimetype: str = None) -> QuerySet:
    """Lista anexos de uma entidade."""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Anexo.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if mimetype:
        qs = qs.filter(mimetype__startswith=mimetype)

    return qs.order_by('-created_at')
