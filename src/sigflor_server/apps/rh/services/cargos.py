# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Cargo, RiscoPadrao


class CargoService:

    @staticmethod
    @transaction.atomic
    def create(
        nome: str,
        nivel: str,
        salario_base: Optional[Decimal] = None,
        cbo: Optional[str] = None,
        descricao: Optional[str] = None,
        risco_fisico: str = RiscoPadrao.FISICO,
        risco_biologico: str = RiscoPadrao.BIOLOGICO,
        risco_quimico: str = RiscoPadrao.QUIMICO,
        risco_ergonomico: str = RiscoPadrao.ERGONOMICO,
        risco_acidente: str = RiscoPadrao.ACIDENTE,
        ativo: bool = True,
        created_by=None,
        documentos_exigidos: list = None, 
        **kwargs
    ) -> Cargo:
        print({"documentos_exigidos": documentos_exigidos})
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

        if documentos_exigidos:
            from .cargo_documento import CargoDocumentoService
            
            for doc_data in documentos_exigidos:
                CargoDocumentoService.configurar_documento_para_cargo(
                    cargo=cargo,
                    documento_tipo=doc_data['documento_tipo'],
                    obrigatorio=doc_data.get('obrigatorio', True),
                    condicional=doc_data.get('condicional'),
                    created_by=created_by
                )

        return cargo

    @staticmethod
    @transaction.atomic
    def update(cargo: Cargo, updated_by=None, **kwargs) -> Cargo:
        for attr, value in kwargs.items():
            if hasattr(cargo, attr):
                setattr(cargo, attr, value)
        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def delete(cargo: Cargo, user=None) -> None:
        if cargo.funcionarios.filter(deleted_at__isnull=True).exists():
            raise ValidationError(
                'Não é possível excluir um cargo com funcionários vinculados.'
            )
        cargo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(cargo: Cargo, updated_by=None) -> Cargo:
        cargo.ativo = True
        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def desativar(cargo: Cargo, updated_by=None) -> Cargo:
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
        return list(Cargo.objects.filter(
            ativo=True,
            deleted_at__isnull=True
        ).order_by('nome'))

    @staticmethod
    def get_cargos_com_risco() -> list:
        return list(Cargo.objects.filter(
            ativo=True,
            deleted_at__isnull=True
        ).exclude(
            risco_fisico=RiscoPadrao.FISICO,
            risco_biologico=RiscoPadrao.BIOLOGICO,
            risco_quimico=RiscoPadrao.QUIMICO,
            risco_ergonomico=RiscoPadrao.ERGONOMICO,
            risco_acidente=RiscoPadrao.ACIDENTE
        ).order_by('nome'))

    @staticmethod
    def get_cargos_por_nivel(nivel: str) -> list:
        """Retorna lista de cargos por nível hierárquico."""
        return list(Cargo.objects.filter(
            nivel=nivel,
            ativo=True,
            deleted_at__isnull=True
        ).order_by('nome'))
