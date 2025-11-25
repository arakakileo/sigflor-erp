# -*- coding: utf-8 -*-
from typing import Optional
from datetime import date
from django.db import transaction

from ..models import SubContrato, Filial, Contrato


class SubContratoService:
    """Service layer para operações com SubContrato."""

    @staticmethod
    @transaction.atomic
    def create(
        filial: Filial,
        contrato: Contrato,
        data_inicio: date,
        descricao: Optional[str] = None,
        data_fim: Optional[date] = None,
        ativo: bool = True,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> SubContrato:
        """Cria um novo SubContrato."""
        subcontrato = SubContrato(
            filial=filial,
            contrato=contrato,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=ativo,
            observacoes=observacoes,
            created_by=created_by,
        )
        subcontrato.save()
        return subcontrato

    @staticmethod
    @transaction.atomic
    def update(subcontrato: SubContrato, updated_by=None, **kwargs) -> SubContrato:
        """Atualiza um SubContrato existente."""
        for attr, value in kwargs.items():
            if hasattr(subcontrato, attr):
                setattr(subcontrato, attr, value)
        subcontrato.updated_by = updated_by
        subcontrato.save()
        return subcontrato

    @staticmethod
    @transaction.atomic
    def delete(subcontrato: SubContrato, user=None) -> None:
        """Soft delete de um SubContrato."""
        subcontrato.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(subcontrato: SubContrato, updated_by=None) -> SubContrato:
        """Ativa um subcontrato."""
        subcontrato.ativo = True
        subcontrato.updated_by = updated_by
        subcontrato.save()
        return subcontrato

    @staticmethod
    @transaction.atomic
    def desativar(subcontrato: SubContrato, updated_by=None) -> SubContrato:
        """Desativa um subcontrato."""
        subcontrato.ativo = False
        subcontrato.updated_by = updated_by
        subcontrato.save()
        return subcontrato

    @staticmethod
    @transaction.atomic
    def transferir_filial(
        subcontrato: SubContrato,
        nova_filial: Filial,
        updated_by=None,
    ) -> SubContrato:
        """Transfere um subcontrato para outra filial."""
        subcontrato.filial = nova_filial
        subcontrato.updated_by = updated_by
        subcontrato.save()
        return subcontrato
