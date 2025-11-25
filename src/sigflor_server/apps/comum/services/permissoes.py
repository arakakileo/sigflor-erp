from typing import Optional
from django.db import transaction

from ..models import Permissao, Papel


class PermissaoService:
    """Service layer para operações com Permissão."""

    @staticmethod
    @transaction.atomic
    def create(
        codigo: str,
        nome: str,
        descricao: Optional[str] = None,
        created_by=None,
    ) -> Permissao:
        """Cria uma nova Permissão."""
        permissao = Permissao(
            codigo=codigo,
            nome=nome,
            descricao=descricao,
            created_by=created_by,
        )
        permissao.save()
        return permissao

    @staticmethod
    @transaction.atomic
    def update(permissao: Permissao, updated_by=None, **kwargs) -> Permissao:
        """Atualiza uma Permissão existente."""
        for attr, value in kwargs.items():
            if hasattr(permissao, attr):
                setattr(permissao, attr, value)
        permissao.updated_by = updated_by
        permissao.save()
        return permissao

    @staticmethod
    @transaction.atomic
    def delete(permissao: Permissao, user=None) -> None:
        """Soft delete de uma Permissão."""
        permissao.delete(user=user)

    @staticmethod
    def get_by_codigo(codigo: str) -> Optional[Permissao]:
        """Busca Permissão por código."""
        return Permissao.objects.filter(
            codigo=codigo,
            deleted_at__isnull=True
        ).first()


class PapelService:
    """Service layer para operações com Papel."""

    @staticmethod
    @transaction.atomic
    def create(
        nome: str,
        descricao: Optional[str] = None,
        permissoes: Optional[list] = None,
        created_by=None,
    ) -> Papel:
        """Cria um novo Papel."""
        papel = Papel(
            nome=nome,
            descricao=descricao,
            created_by=created_by,
        )
        papel.save()
        if permissoes:
            papel.permissoes.set(permissoes)
        return papel

    @staticmethod
    @transaction.atomic
    def update(papel: Papel, updated_by=None, **kwargs) -> Papel:
        """Atualiza um Papel existente."""
        permissoes = kwargs.pop('permissoes', None)
        for attr, value in kwargs.items():
            if hasattr(papel, attr):
                setattr(papel, attr, value)
        papel.updated_by = updated_by
        papel.save()
        if permissoes is not None:
            papel.permissoes.set(permissoes)
        return papel

    @staticmethod
    @transaction.atomic
    def delete(papel: Papel, user=None) -> None:
        """Soft delete de um Papel."""
        papel.delete(user=user)

    @staticmethod
    @transaction.atomic
    def adicionar_permissao(papel: Papel, permissao: Permissao) -> None:
        """Adiciona uma permissão ao papel."""
        papel.permissoes.add(permissao)

    @staticmethod
    @transaction.atomic
    def remover_permissao(papel: Papel, permissao: Permissao) -> None:
        """Remove uma permissão do papel."""
        papel.permissoes.remove(permissao)
