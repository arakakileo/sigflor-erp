from typing import Optional
from django.db import transaction

from ..models import Papel, Usuario

class PapelService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        permissoes: Optional[list] = None,
        **kwargs
    ) -> Papel:
        papel = Papel(
            created_by=user,
            **kwargs
        )
        papel.save()
        if permissoes:
            papel.permissoes.set(permissoes)
        return papel

    @staticmethod
    @transaction.atomic
    def update(
        *,
        user: Usuario,
        papel: Papel,
        **kwargs
    ) -> Papel:
        for attr, value in kwargs.items():
            if hasattr(papel, attr):
                setattr(papel, attr, value)
        papel.updated_by = user
        papel.save()
        return papel

    @staticmethod
    @transaction.atomic
    def delete(user: Usuario , papel: Papel) -> None:
        papel.delete(user=user)

    @staticmethod
    @transaction.atomic
    def adicionar_permissoes(*, user: Usuario, papel: Papel, permissoes: list) -> None:
        papel.permissoes.add(*permissoes)
        papel.updated_by = user
        papel.save()

    @staticmethod
    @transaction.atomic
    def remover_permissoes(*, user: Usuario, papel: Papel, permissoes: list) -> None:
        papel.permissoes.remove(*permissoes)
        papel.updated_by = user
        papel.save()