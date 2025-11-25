# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from datetime import date
from django.db import transaction

from ..models import Contrato, Contratante, EmpresaCNPJ


class ContratoService:
    """Service layer para operações com Contrato."""

    @staticmethod
    @transaction.atomic
    def create(
        numero_interno: str,
        contratante: Contratante,
        empresa: EmpresaCNPJ,
        data_inicio: date,
        numero_externo: Optional[str] = None,
        descricao: Optional[str] = None,
        data_fim: Optional[date] = None,
        ativo: bool = True,
        valor: Optional[Decimal] = None,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> Contrato:
        """Cria um novo Contrato."""
        contrato = Contrato(
            numero_interno=numero_interno,
            numero_externo=numero_externo,
            contratante=contratante,
            empresa=empresa,
            descricao=descricao,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=ativo,
            valor=valor,
            observacoes=observacoes,
            created_by=created_by,
        )
        contrato.save()
        return contrato

    @staticmethod
    @transaction.atomic
    def update(contrato: Contrato, updated_by=None, **kwargs) -> Contrato:
        """Atualiza um Contrato existente."""
        for attr, value in kwargs.items():
            if hasattr(contrato, attr):
                setattr(contrato, attr, value)
        contrato.updated_by = updated_by
        contrato.save()
        return contrato

    @staticmethod
    @transaction.atomic
    def delete(contrato: Contrato, user=None) -> None:
        """Soft delete de um Contrato."""
        contrato.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(contrato: Contrato, updated_by=None) -> Contrato:
        """Ativa um contrato."""
        contrato.ativo = True
        contrato.updated_by = updated_by
        contrato.save()
        return contrato

    @staticmethod
    @transaction.atomic
    def desativar(contrato: Contrato, updated_by=None) -> Contrato:
        """Desativa um contrato."""
        contrato.ativo = False
        contrato.updated_by = updated_by
        contrato.save()
        return contrato

    @staticmethod
    @transaction.atomic
    def renovar(
        contrato: Contrato,
        nova_data_fim: date,
        novo_valor: Optional[Decimal] = None,
        updated_by=None,
    ) -> Contrato:
        """Renova um contrato estendendo a data de fim."""
        contrato.data_fim = nova_data_fim
        if novo_valor is not None:
            contrato.valor = novo_valor
        contrato.ativo = True
        contrato.updated_by = updated_by
        contrato.save()
        return contrato
