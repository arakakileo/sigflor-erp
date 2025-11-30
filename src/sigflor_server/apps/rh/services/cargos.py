# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Cargo


class CargoService:
    """Service layer para operações com Cargo."""

    @staticmethod
    @transaction.atomic
    def create(
        nome: str,
        nivel: str,
        salario_base: Optional[Decimal] = None,
        cbo: Optional[str] = None,
        descricao: Optional[str] = None,
        risco_fisico: bool = False,
        risco_biologico: bool = False,
        risco_quimico: bool = False,
        risco_ergonomico: bool = False,
        risco_acidente: bool = False,
        ativo: bool = True,
        created_by=None,
        **kwargs
    ) -> Cargo:
        """Cria um novo Cargo."""
        cargo = Cargo(
            nome=nome,
            nivel=nivel,
            salario_base=salario_base,
            cbo=cbo,
            descricao=descricao,
            risco_fisico=risco_fisico,
            risco_biologico=risco_biologico,
            risco_quimico=risco_quimico,
            risco_ergonomico=risco_ergonomico,
            risco_acidente=risco_acidente,
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
        # Verifica se existem funcionários vinculados
        if cargo.funcionarios.filter(deleted_at__isnull=True).exists():
            raise ValidationError(
                'Não é possível excluir um cargo com funcionários vinculados.'
            )
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

    @staticmethod
    @transaction.atomic
    def atualizar_riscos(
        cargo: Cargo,
        risco_fisico: Optional[bool] = None,
        risco_biologico: Optional[bool] = None,
        risco_quimico: Optional[bool] = None,
        risco_ergonomico: Optional[bool] = None,
        risco_acidente: Optional[bool] = None,
        updated_by=None
    ) -> Cargo:
        """Atualiza os indicadores de risco do cargo."""
        if risco_fisico is not None:
            cargo.risco_fisico = risco_fisico
        if risco_biologico is not None:
            cargo.risco_biologico = risco_biologico
        if risco_quimico is not None:
            cargo.risco_quimico = risco_quimico
        if risco_ergonomico is not None:
            cargo.risco_ergonomico = risco_ergonomico
        if risco_acidente is not None:
            cargo.risco_acidente = risco_acidente

        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    def get_cargos_ativos() -> list:
        """Retorna lista de cargos ativos."""
        return list(Cargo.objects.filter(
            ativo=True,
            deleted_at__isnull=True
        ).order_by('nome'))

    @staticmethod
    def get_cargos_com_risco() -> list:
        """Retorna lista de cargos com algum tipo de risco."""
        from django.db.models import Q
        return list(Cargo.objects.filter(
            Q(risco_fisico=True) |
            Q(risco_biologico=True) |
            Q(risco_quimico=True) |
            Q(risco_ergonomico=True) |
            Q(risco_acidente=True),
            ativo=True,
            deleted_at__isnull=True
        ).order_by('nome'))

    @staticmethod
    def get_cargos_por_nivel(nivel: str) -> list:
        """Retorna lista de cargos por nível hierárquico."""
        return list(Cargo.objects.filter(
            nivel=nivel,
            ativo=True,
            deleted_at__isnull=True
        ).order_by('nome'))
