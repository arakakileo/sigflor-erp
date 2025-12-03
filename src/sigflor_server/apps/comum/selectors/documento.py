from django.db.models import QuerySet, Q
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from ..models import Documento

def documento_list_por_entidade(*, entidade, tipo: str = None, vencidos: bool = None) -> QuerySet:
    """Lista documentos de uma entidade. (FIXME: Lógica de GFK pode precisar de revisão)"""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Documento.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if tipo:
        qs = qs.filter(tipo=tipo)

    if vencidos is True:
        qs = qs.filter(data_validade__lt=timezone.now().date())
    elif vencidos is False:
        qs = qs.filter(
            Q(data_validade__isnull=True) |
            Q(data_validade__gte=timezone.now().date())
        )

    return qs.order_by('tipo', '-principal', '-created_at')
