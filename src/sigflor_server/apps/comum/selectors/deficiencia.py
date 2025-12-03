from django.db.models import QuerySet, Q, Count
from ..models import Deficiencia, PessoaFisica

def deficiencia_list(
    *,
    pessoa_fisica_id: str = None,
    search: str = None,
    tipo: str = None,
    cid: str = None
) -> QuerySet:
    """Lista deficiencias com filtros opcionais."""
    qs = Deficiencia.objects.filter(
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if pessoa_fisica_id:
        qs = qs.filter(pessoa_fisica_id=pessoa_fisica_id)

    if tipo:
        qs = qs.filter(tipo=tipo)

    if cid:
        qs = qs.filter(cid__icontains=cid)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(cid__icontains=search) |
            Q(pessoa_fisica__nome_completo__icontains=search)
        )

    return qs.order_by('pessoa_fisica__nome_completo', 'nome')


def deficiencia_detail(*, pk) -> Deficiencia:
    """Obtem detalhes de uma deficiencia."""
    return Deficiencia.objects.select_related(
        'pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)


def deficiencias_por_pessoa(*, pessoa_fisica_id: str) -> QuerySet:
    """Lista deficiencias de uma pessoa fisica especifica."""
    return Deficiencia.objects.filter(
        pessoa_fisica_id=pessoa_fisica_id,
        deleted_at__isnull=True
    ).order_by('nome')


def pessoas_com_deficiencia() -> QuerySet:
    """Lista pessoas fisicas que possuem deficiencias."""
    return PessoaFisica.objects.filter(
        possui_deficiencia=True,
        deleted_at__isnull=True
    ).order_by('nome_completo')


def estatisticas_deficiencias() -> dict:
    """Retorna estatisticas de deficiencias."""
    qs = Deficiencia.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    congenitas = qs.filter(congenita=True).count()

    por_tipo = qs.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')

    pessoas_com_def = PessoaFisica.objects.filter(
        possui_deficiencia=True,
        deleted_at__isnull=True
    ).count()

    return {
        'total_deficiencias': total,
        'congenitas': congenitas,
        'adquiridas': total - congenitas,
        'por_tipo': list(por_tipo),
        'pessoas_com_deficiencia': pessoas_com_def,
    }
