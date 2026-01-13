from typing import Optional
from django.db.models import QuerySet, Q, Count
from rest_framework.exceptions import PermissionDenied

from apps.autenticacao.models.usuarios import Usuario
from ..models import Filial

def filial_list(
    *,
    user: Usuario,
    filters: Optional[dict]= None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    empresa_id: Optional[str] = None
) -> QuerySet:
    qs = Filial.objects.filter(deleted_at__isnull=True)

    # if not user.is_superuser:
    #     qs = qs.filter(id__in=user.allowed_filiais.all()) # Filtra por filiais permitidas ao usuario

    qs = qs.select_related('empresa')

    if status:
        qs = qs.filter(status=status)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(codigo_interno__icontains=search)
        )

    return qs.order_by('nome')


def filial_detail(*, user: Usuario, pk) -> Filial:
    filial = Filial.objects.select_related(
        'empresa', 'empresa__pessoa_juridica'
    ).prefetch_related(
        'enderecos_vinculados__endereco',
        'contatos_vinculados__contato'
    ).get(pk=pk, deleted_at__isnull=True)

    # if not user.is_superuser:
    #     if not user.allowed_filiais.filter(id=filial.id).exists():
    #         raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
    
    return filial


def filial_get_by_id_irrestrito(*, pk: str) -> Optional[Filial]:
    return Filial.objects.filter(pk=pk).first()


def estatisticas_filiais(*, user: Usuario) -> dict:
    qs = Filial.objects.filter(deleted_at__isnull=True)

    # if not user.is_superuser:
    #     qs = qs.filter(id__in=user.allowed_filiais.all())

    total = qs.count()

    por_status = qs.values('status').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total': total,
        'por_status': list(por_status),
    }


def filial_list_selection(*, user, ativa: bool = True) -> QuerySet:
    qs = Filial.objects.filter(
        deleted_at__isnull=True,
    )
    
    if ativa:
        qs = qs.filter(status=Filial.Status.ATIVA)

    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all())

    return qs.only('id', 'nome', 'codigo_interno').order_by('nome')