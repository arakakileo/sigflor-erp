from django.db.models import QuerySet, Q
from ..models import Cliente

def cliente_list(
    *,
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista clientes com filtros opcionais."""
    qs = Cliente.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica', 'empresa_gestora')

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if empresa_id:
        qs = qs.filter(empresa_gestora_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(pessoa_juridica__razao_social__icontains=search) |
            Q(pessoa_juridica__nome_fantasia__icontains=search) |
            Q(pessoa_juridica__cnpj__icontains=search)
        )

    return qs.order_by('pessoa_juridica__razao_social')


def cliente_detail(*, pk) -> Cliente:
    """Obtem detalhes de um cliente com relacionamentos."""
    return Cliente.objects.select_related(
        'pessoa_juridica', 'empresa_gestora'
    ).prefetch_related(
        'pessoa_juridica__enderecos_vinculados__endereco',
        'pessoa_juridica__contatos_vinculados__contato',
        'pessoa_juridica__documentos_vinculados__documento'
    ).get(pk=pk, deleted_at__isnull=True)
