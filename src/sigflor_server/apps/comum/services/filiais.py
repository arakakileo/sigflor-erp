# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction

from ..models import Filial, EmpresaCNPJ


class FilialService:
    """Service layer para operações com Filial."""

    @staticmethod
    @transaction.atomic
    def create(
        nome: str,
        codigo_interno: str,
        empresa: Optional[EmpresaCNPJ] = None,
        status: str = Filial.Status.ATIVA,
        descricao: Optional[str] = None,
        created_by=None,
    ) -> Filial:
        """Cria uma nova Filial."""
        filial = Filial(
            nome=nome,
            codigo_interno=codigo_interno,
            empresa=empresa,
            status=status,
            descricao=descricao,
            created_by=created_by,
        )
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def update(filial: Filial, updated_by=None, **kwargs) -> Filial:
        """Atualiza uma Filial existente."""
        for attr, value in kwargs.items():
            if hasattr(filial, attr):
                setattr(filial, attr, value)
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def delete(filial: Filial, user=None) -> None:
        """Soft delete de uma Filial."""
        filial.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(filial: Filial, updated_by=None) -> Filial:
        """Ativa uma filial."""
        filial.status = Filial.Status.ATIVA
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def desativar(filial: Filial, updated_by=None) -> Filial:
        """Desativa uma filial."""
        filial.status = Filial.Status.INATIVA
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def suspender(filial: Filial, updated_by=None) -> Filial:
        """Suspende uma filial."""
        filial.status = Filial.Status.SUSPENSA
        filial.updated_by = updated_by
        filial.save()
        return filial
