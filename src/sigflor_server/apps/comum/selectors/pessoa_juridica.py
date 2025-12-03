from django.db.models import QuerySet, Q
from ..models import PessoaJuridica

def pessoa_juridica_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista pessoas juridicas com filtros opcionais."""
    qs = PessoaJuridica.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(razao_social__icontains=search) |
            Q(nome_fantasia__icontains=search) |
            Q(cnpj__icontains=search)
        )

    return qs.order_by('razao_social')


def pessoa_juridica_detail(*, pk) -> PessoaJuridica:
    """Obtem detalhes de uma pessoa juridica com relacionamentos."""
    return PessoaJuridica.objects.prefetch_related(
        'enderecos_vinculados__endereco',
        'contatos_vinculados__contato',
        'documentos_vinculados__documento'
    ).get(pk=pk, deleted_at__isnull=True)
