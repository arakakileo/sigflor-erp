from typing import Optional
from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied

from ..models import Projeto, StatusProjeto, Cliente, Filial, Contrato, Usuario


class ProjetoService:
    """Service layer para operações com Projeto."""

    @staticmethod
    def _check_filial_access(user: Usuario, filial: Filial) -> bool:
        """
        Verifica se o usuário tem acesso à filial.
        Superusuários sempre têm acesso.
        """
        if user.is_superuser:
            return True
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
        return True

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        descricao: str,
        cliente_id: UUID,
        filial_id: UUID,
        data_inicio,
        contrato_id: Optional[UUID] = None,
        data_fim=None,
        status: str = StatusProjeto.PLANEJADO,
    ) -> Projeto:
        """
        Cria um novo Projeto.
        O número é gerado automaticamente.
        A empresa é preenchida automaticamente via cliente.empresa_gestora.
        """
        cliente = Cliente.objects.get(id=cliente_id, deleted_at__isnull=True)
        filial = Filial.objects.get(id=filial_id, deleted_at__isnull=True)

        # Verificar permissão regional
        ProjetoService._check_filial_access(user, filial)

        contrato = None
        if contrato_id:
            contrato = Contrato.objects.get(id=contrato_id, deleted_at__isnull=True)

        projeto = Projeto(
            descricao=descricao,
            cliente=cliente,
            filial=filial,
            contrato=contrato,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            created_by=user,
        )
        # empresa e numero são preenchidos automaticamente no save()
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def update(
        *,
        user: Usuario,
        projeto: Projeto,
        **kwargs
    ) -> Projeto:
        """
        Atualiza um Projeto existente.
        Não permite alterar cliente (e consequentemente empresa).
        """
        # Verificar permissão na filial atual
        ProjetoService._check_filial_access(user, projeto.filial)

        # Se mudando de filial, verificar permissão na nova
        filial_id = kwargs.pop('filial_id', None)
        if filial_id and filial_id != projeto.filial_id:
            nova_filial = Filial.objects.get(id=filial_id, deleted_at__isnull=True)
            ProjetoService._check_filial_access(user, nova_filial)
            projeto.filial = nova_filial

        # Atualizar contrato se fornecido
        contrato_id = kwargs.pop('contrato_id', None)
        if contrato_id is not None:
            if contrato_id:
                projeto.contrato = Contrato.objects.get(id=contrato_id, deleted_at__isnull=True)
            else:
                projeto.contrato = None

        # Atualizar outros campos
        allowed_fields = ['descricao', 'data_inicio', 'data_fim', 'status']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(projeto, field):
                setattr(projeto, field, value)

        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def delete(*, user: Usuario, projeto: Projeto) -> None:
        """Soft delete de um Projeto."""
        ProjetoService._check_filial_access(user, projeto.filial)
        projeto.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(*, user: Usuario, projeto: Projeto) -> Projeto:
        """Restaura um Projeto excluído."""
        ProjetoService._check_filial_access(user, projeto.filial)
        projeto.restore(user=user)
        return projeto

    @staticmethod
    @transaction.atomic
    def change_status(
        *,
        user: Usuario,
        projeto: Projeto,
        novo_status: str
    ) -> Projeto:
        """Altera o status de um Projeto."""
        ProjetoService._check_filial_access(user, projeto.filial)

        projeto.status = novo_status
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    def get_by_numero(numero: str) -> Optional[Projeto]:
        """Busca Projeto pelo número."""
        return Projeto.objects.filter(
            numero=numero,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def list_ativos(user: Optional[Usuario] = None) -> QuerySet:
        """
        Lista projetos em execução.
        Se user fornecido, filtra por filiais permitidas.
        """
        qs = Projeto.objects.filter(
            status=StatusProjeto.EM_EXECUCAO,
            deleted_at__isnull=True
        ).select_related('cliente', 'empresa', 'filial', 'contrato')

        if user and not user.is_superuser:
            qs = qs.filter(filial__in=user.allowed_filiais.all())

        return qs.order_by('-created_at')

    @staticmethod
    def list_by_cliente(cliente_id: UUID) -> QuerySet:
        """Lista projetos de um cliente."""
        return Projeto.objects.filter(
            cliente_id=cliente_id,
            deleted_at__isnull=True
        ).select_related('empresa', 'filial', 'contrato').order_by('-created_at')

    @staticmethod
    def list_by_filial(filial_id: UUID) -> QuerySet:
        """Lista projetos de uma filial."""
        return Projeto.objects.filter(
            filial_id=filial_id,
            deleted_at__isnull=True
        ).select_related('cliente', 'empresa', 'contrato').order_by('-created_at')

    @staticmethod
    def list_by_empresa(empresa_id: UUID) -> QuerySet:
        """Lista projetos de uma empresa."""
        return Projeto.objects.filter(
            empresa_id=empresa_id,
            deleted_at__isnull=True
        ).select_related('cliente', 'filial', 'contrato').order_by('-created_at')
