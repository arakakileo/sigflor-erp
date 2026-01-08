from typing import Optional
from django.db.models import QuerySet, Q
from ..models import Cliente
from apps.autenticacao.models.usuarios import Usuario

def cliente_list(
    *,
    user: Usuario,
    filters: Optional[dict] = None,
    search: Optional[str] = None,
    ativo: Optional[bool] = None,
    empresa_id: Optional[str] = None
) -> QuerySet:
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

def cliente_get_by_id_irrestrito(*, user: Usuario, pk: str) -> Optional[Cliente]:
    return Cliente.objects.filter(pk=pk).select_related('pessoa_juridica').first()

def cliente_detail(*, user: Usuario, pk) -> Cliente:
    return Cliente.objects.select_related(
        'pessoa_juridica', 'empresa_gestora'
    ).prefetch_related(
        'pessoa_juridica__enderecos_vinculados__endereco',
        'pessoa_juridica__contatos_vinculados__contato',
        'pessoa_juridica__documentos_vinculados__documento'
    ).get(pk=pk, deleted_at__isnull=True)

def cliente_list_selection(*, user: Usuario, ativo: bool = True) -> QuerySet:
    qs = Cliente.objects.filter(
        deleted_at__isnull=True,
        ativo=ativo
    ).select_related('pessoa_juridica').only(
        'id', 
        'pessoa_juridica__razao_social', 
        'pessoa_juridica__cnpj'
    )
    
    return qs.order_by('pessoa_juridica__razao_social')