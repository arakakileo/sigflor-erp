from typing import Optional
from django.db.models import QuerySet, Q

from ..models import Empresa
from apps.autenticacao.models.usuarios import Usuario


def empresa_list(
        *,
        user: Usuario,
        filters: Optional[dict] = None, 
        search: Optional[str] = None, 
        ativa: Optional[bool] = None
) -> QuerySet:
    qs = Empresa.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica')

    if ativa is not None:
        qs = qs.filter(ativa=ativa)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(pessoa_juridica__razao_social__icontains=search) |
            Q(pessoa_juridica__cnpj__icontains=search)
        )

    return qs.order_by('pessoa_juridica__razao_social')

def empresa_get_by_id_irrestrito(*, user: Usuario, pk: str) -> Optional[Empresa]:
    """
    Busca uma empresa pelo ID, ignorando o soft delete.
    Retorna None se não encontrar.
    Usado principalmente para operações de restore ou admin.
    """
    return Empresa.objects.filter(pk=pk).select_related('pessoa_juridica').first()

def empresa_detail(*, user: Usuario, pk) -> Empresa:
    return Empresa.objects.select_related(
        'pessoa_juridica'
    ).prefetch_related(
        'pessoa_juridica__enderecos_vinculados__endereco',
        'pessoa_juridica__contatos_vinculados__contato',
        'pessoa_juridica__documentos_vinculados__documento'
    ).get(pk=pk, deleted_at__isnull=True)

def empresa_list_selection(*, user: Usuario, ativa: bool = True) -> QuerySet:

    qs = Empresa.objects.filter(
        deleted_at__isnull=True,
        ativa=ativa
    ).select_related(
        'pessoa_juridica'
    ).only(
        'id',
        'pessoa_juridica__razao_social',
        'pessoa_juridica__cnpj'
    )

    return qs.order_by('pessoa_juridica__razao_social')