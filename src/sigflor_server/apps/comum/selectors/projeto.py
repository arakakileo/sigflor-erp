from django.db.models import QuerySet, Q
from rest_framework.exceptions import PermissionDenied
from typing import Optional
from uuid import UUID

from apps.autenticacao.models.usuarios import Usuario
from ..models import Projeto, StatusProjeto

def projeto_list(
    *,
    user: Usuario,
    search: Optional[str],
    ativo: Optional[bool],
    filial_id: Optional[UUID],
    cliente_id: Optional[UUID],
    empresa_id: Optional[UUID]
) -> QuerySet:
    
    qs = Projeto.objects.filter(deleted_at__isnull=True).select_related(
        'cliente__pessoa_juridica', 
        'filial', 
        'empresa__pessoa_juridica'
    )

    if ativo is not None:
        if ativo:
            qs = qs.filter(status=StatusProjeto.EM_EXECUCAO)
        else:
            qs = qs.exclude(status=StatusProjeto.EM_EXECUCAO)

    if filial_id:
        qs = qs.filter(filial_id=filial_id)
    
    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if search:
        qs = qs.filter(
            Q(numero__icontains=search) |
            Q(descricao__icontains=search) |
            Q(cliente__pessoa_juridica__nome_fantasia__icontains=search) |
            Q(filial__nome__icontains=search)
        )

    # Permissão Regional (Opcional, descomentar se necessário)
    # if not user.is_superuser:
    #     qs = qs.filter(filial__in=user.allowed_filiais.all())

    return qs.order_by('-created_at')

def projeto_detail(*, user: Usuario, pk) -> Projeto:
    projeto = Projeto.objects.select_related(
        'cliente', 'filial', 'empresa',
        'cliente__pessoa_juridica', 'empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)

    # if not user.is_superuser:
    #     if not user.allowed_filiais.filter(id=projeto.filial.id).exists():
    #         raise PermissionDenied(f"Usuário não tem acesso a este projeto.")

    return projeto

def projeto_list_selection(*, user, ativo: bool = True) -> QuerySet:
    qs = Projeto.objects.filter(deleted_at__isnull=True)
    
    if ativo:
        qs = qs.filter(status=StatusProjeto.EM_EXECUCAO)
        
    if not user.is_superuser:
        qs = qs.filter(filial__in=user.allowed_filiais.all())

    return qs.only('id', 'numero', 'descricao').order_by('descricao')

def projeto_get_by_id_irrestrito(*, pk: str) -> Optional[Projeto]:
    return Projeto.objects.filter(pk=pk).first()