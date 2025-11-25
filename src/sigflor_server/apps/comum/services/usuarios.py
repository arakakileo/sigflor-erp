from typing import Optional
from django.db import transaction

from ..models import Usuario, Papel, Permissao


class UsuarioService:
    """Service layer para operações com Usuário."""

    @staticmethod
    @transaction.atomic
    def create(
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        pessoa_fisica=None,
        ativo: bool = True,
        is_staff: bool = False,
        is_superuser: bool = False,
    ) -> Usuario:
        """Cria um novo Usuário."""
        usuario = Usuario(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            pessoa_fisica=pessoa_fisica,
            ativo=ativo,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        usuario.set_password(password)
        usuario.save()
        return usuario

    @staticmethod
    @transaction.atomic
    def update(usuario: Usuario, **kwargs) -> Usuario:
        """Atualiza um Usuário existente."""
        password = kwargs.pop('password', None)
        for attr, value in kwargs.items():
            if hasattr(usuario, attr):
                setattr(usuario, attr, value)
        if password:
            usuario.set_password(password)
        usuario.save()
        return usuario

    @staticmethod
    @transaction.atomic
    def delete(usuario: Usuario, user=None) -> None:
        """Soft delete de um Usuário."""
        usuario.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(usuario: Usuario) -> Usuario:
        """Restaura um Usuário excluído."""
        usuario.restore()
        return usuario

    @staticmethod
    @transaction.atomic
    def atribuir_papel(usuario: Usuario, papel: Papel) -> None:
        """Atribui um papel ao usuário."""
        usuario.papeis.add(papel)

    @staticmethod
    @transaction.atomic
    def remover_papel(usuario: Usuario, papel: Papel) -> None:
        """Remove um papel do usuário."""
        usuario.papeis.remove(papel)

    @staticmethod
    @transaction.atomic
    def atribuir_permissao_direta(usuario: Usuario, permissao: Permissao) -> None:
        """Atribui uma permissão direta ao usuário."""
        usuario.permissoes_diretas.add(permissao)

    @staticmethod
    @transaction.atomic
    def remover_permissao_direta(usuario: Usuario, permissao: Permissao) -> None:
        """Remove uma permissão direta do usuário."""
        usuario.permissoes_diretas.remove(permissao)

    @staticmethod
    @transaction.atomic
    def reset_senha(usuario: Usuario, nova_senha: str) -> Usuario:
        """Reseta a senha do usuário."""
        usuario.set_password(nova_senha)
        usuario.save()
        return usuario

    @staticmethod
    def get_by_username(username: str) -> Optional[Usuario]:
        """Busca Usuário por username."""
        return Usuario.objects.filter(
            username=username,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_by_email(email: str) -> Optional[Usuario]:
        """Busca Usuário por email."""
        return Usuario.objects.filter(
            email=email,
            deleted_at__isnull=True
        ).first()
