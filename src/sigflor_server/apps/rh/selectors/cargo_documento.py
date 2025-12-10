from django.db.models import QuerySet

from ..models import CargoDocumento
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# CargoDocumento Selectors
# ============================================================================

def cargo_documento_list(*, user: Usuario, cargo_id: str = None, apenas_obrigatorios: bool = False) -> QuerySet:
    """Lista documentos de cargo."""
    qs = CargoDocumento.objects.filter(deleted_at__isnull=True).select_related('cargo')

    if cargo_id:
        qs = qs.filter(cargo_id=cargo_id)

    if apenas_obrigatorios:
        qs = qs.filter(obrigatorio=True)

    return qs.order_by('cargo__nome', 'documento_tipo')

def cargo_documento_detail(*, user: Usuario, pk) -> CargoDocumento:
    cargo_doc = CargoDocumento.objects.select_related('cargo').get(pk=pk, deleted_at__isnull=True)
    return cargo_doc