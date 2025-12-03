from django.db.models import QuerySet, Q
from ..models import PessoaFisica, Endereco, Contato, Documento

def pessoa_fisica_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista pessoas fisicas com filtros opcionais."""
    qs = PessoaFisica.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome_completo__icontains=search) |
            Q(cpf__icontains=search)
        )

    return qs.order_by('nome_completo')


def pessoa_fisica_detail(*, pk) -> PessoaFisica:
    """Obtem detalhes de uma pessoa fisica com relacionamentos."""
    return PessoaFisica.objects.prefetch_related(
        'enderecos_vinculados__endereco',
        'contatos_vinculados__contato',
        'documentos_vinculados__documento'
    ).get(pk=pk, deleted_at__isnull=True)
