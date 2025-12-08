from django.db.models import QuerySet, Q
from rest_framework.exceptions import PermissionDenied
from typing import Optional
from uuid import UUID

from apps.autenticacao.models.usuarios import Usuario
from ..models import Projeto, StatusProjeto

def projeto_list(
    *,
    user: Usuario,
    filters: dict = None,
    search: str = None
) -> QuerySet:
    qs = Projeto.objects.filter(deleted_at__isnull=True).select_related('cliente__pessoa_juridica', 'filial', 'empresa__pessoa_juridica')

    # if not user.is_superuser:
    #     qs = qs.filter(filial__in=user.allowed_filiais.all()).distinct()

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(numero__icontains=search) |
            Q(cliente__pessoa_juridica__nome_fantasia__icontains=search) |
            Q(filial__nome__icontains=search)
        )

    return qs.order_by('numero')

def projeto_detail(
    *,
    user: Usuario,
    pk
) -> Projeto:
    projeto = Projeto.objects.select_related(
        'cliente', 'filial', 'empresa',
        'cliente__pessoa_juridica', 'empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=projeto.filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso ao projeto {projeto.numero} via filial {projeto.filial.nome}.")

    return projeto

def get_by_numero(numero: str) -> Optional[Projeto]:
    return Projeto.objects.filter(
        numero=numero,
        deleted_at__isnull=True
    ).first()

def list_ativos(user: Optional[Usuario] = None) -> QuerySet:
    qs = Projeto.objects.filter(
        status=StatusProjeto.EM_EXECUCAO,
        deleted_at__isnull=True
    ).select_related('cliente', 'empresa', 'filial')

    if user and not user.is_superuser:
        qs = qs.filter(filial__in=user.allowed_filiais.all())

    return qs.order_by('-created_at')

def list_by_cliente(cliente_id: UUID) -> QuerySet:
    return Projeto.objects.filter(
        cliente_id=cliente_id,
        deleted_at__isnull=True
    ).select_related('empresa', 'filial').order_by('-created_at')

def list_by_filial(filial_id: UUID) -> QuerySet:
    return Projeto.objects.filter(
        filial_id=filial_id,
        deleted_at__isnull=True
    ).select_related('cliente', 'empresa').order_by('-created_at')

def list_by_empresa(empresa_id: UUID) -> QuerySet:
    return Projeto.objects.filter(
        empresa_id=empresa_id,
        deleted_at__isnull=True
    ).select_related('cliente', 'filial').order_by('-created_at')