from django.db.models import QuerySet
from django.contrib.contenttypes.models import ContentType
from ..models import Contato

def contato_list_por_entidade(*, entidade, tipo: str = None) -> QuerySet:
    """Lista contatos de uma entidade. (FIXME: Lógica de GFK pode precisar de revisão)"""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Contato.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if tipo:
        qs = qs.filter(tipo=tipo)

    return qs.order_by('tipo', '-principal', '-created_at')
