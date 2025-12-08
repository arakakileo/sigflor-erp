from uuid import UUID
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from apps.autenticacao.models.usuarios import Usuario
from ..models import Projeto, StatusProjeto, Cliente, Filial


class ProjetoService:

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

        ProjetoService._check_filial_access(user, filial)

        projeto = Projeto(
            descricao=descricao,
            cliente=cliente,
            filial=filial,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status=status,
            created_by=user,
        )
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

        ProjetoService._check_filial_access(user, projeto.filial)

        filial_id = kwargs.pop('filial_id', None)
        if filial_id and filial_id != projeto.filial_id:
            nova_filial = Filial.objects.get(id=filial_id, deleted_at__isnull=True)
            ProjetoService._check_filial_access(user, nova_filial)
            projeto.filial = nova_filial

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
        ProjetoService._check_filial_access(user, projeto.filial)
        projeto.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(*, user: Usuario, projeto: Projeto) -> Projeto:
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
        ProjetoService._check_filial_access(user, projeto.filial)

        projeto.status = novo_status
        projeto.updated_by = user
        projeto.save()
        return projeto