# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction

from ..models import Cargo


class CargoService:
    """Service layer para operacoes com Cargo."""

    @staticmethod
    @transaction.atomic
    def create(
        nome: str,
        salario: Optional[Decimal] = None,
        cbo: Optional[str] = None,
        descricao: Optional[str] = None,
        nivel: Optional[str] = None,
        ativo: bool = True,
        created_by=None,
    ) -> Cargo:
        """Cria um novo Cargo."""
        cargo = Cargo(
            nome=nome,
            salario=salario,
            cbo=cbo,
            descricao=descricao,
            nivel=nivel,
            ativo=ativo,
            created_by=created_by,
        )
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def update(cargo: Cargo, updated_by=None, **kwargs) -> Cargo:
        """Atualiza um Cargo existente."""
        for attr, value in kwargs.items():
            if hasattr(cargo, attr):
                setattr(cargo, attr, value)
        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def delete(cargo: Cargo, user=None) -> None:
        """Soft delete de um Cargo."""
        # Verifica se existem funcionarios vinculados
        if cargo.funcionarios.filter(deleted_at__isnull=True).exists():
            raise ValueError('Nao e possivel excluir um cargo com funcionarios vinculados.')
        cargo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(cargo: Cargo, updated_by=None) -> Cargo:
        """Ativa um cargo."""
        cargo.ativo = True
        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def desativar(cargo: Cargo, updated_by=None) -> Cargo:
        """Desativa um cargo."""
        cargo.ativo = False
        cargo.updated_by = updated_by
        cargo.save()
        return cargo
