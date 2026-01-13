from typing import Optional
from django.db.models import QuerySet, Q
from ..models import Deficiencia, PessoaFisicaDeficiencia

def deficiencia_list(
    *,
    search: Optional[str] = None,
    tipo: Optional[str] = None,
    cid: Optional[str] = None
) -> QuerySet[Deficiencia]:
    qs = Deficiencia.objects.filter(deleted_at__isnull=True)

    if tipo:
        qs = qs.filter(tipo=tipo)

    if cid:
        qs = qs.filter(cid__icontains=cid)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(cid__icontains=search)
        )

    return qs.order_by('nome')


def deficiencia_detail(*, pk) -> Deficiencia:
    return Deficiencia.objects.get(pk=pk, deleted_at__isnull=True)


def deficiencia_get_by_id_irrestrito(*, pk: str) -> Optional[Deficiencia]:
    return Deficiencia.objects.filter(pk=pk).first()


def deficiencias_por_pessoa(*, pessoa_fisica_id: str) -> QuerySet[PessoaFisicaDeficiencia]:
    return PessoaFisicaDeficiencia.objects.filter(
        pessoa_fisica_id=pessoa_fisica_id,
        deleted_at__isnull=True
    ).select_related('deficiencia').order_by('deficiencia__nome')


def deficiencia_list_selection() -> QuerySet[Deficiencia]:
    return Deficiencia.objects.filter(
        deleted_at__isnull=True
    ).only('id', 'nome', 'cid', 'tipo').order_by('nome')