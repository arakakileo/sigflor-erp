# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction

from ..models import Funcionario, Dependente


class DependenteService:
    """Service layer para operacoes com Dependente."""

    @staticmethod
    @transaction.atomic
    def create(
        funcionario: Funcionario,
        created_by=None,
        **kwargs
    ) -> Dependente:
        """Cria um novo dependente para um funcionario."""
        dependente = Dependente(
            funcionario=funcionario,
            created_by=created_by,
            **kwargs
        )
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def update(dependente: Dependente, updated_by=None, **kwargs) -> Dependente:
        """Atualiza um dependente existente."""
        for attr, value in kwargs.items():
            if hasattr(dependente, attr):
                setattr(dependente, attr, value)

        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def delete(dependente: Dependente, user=None) -> None:
        """Soft delete de um dependente."""
        dependente.delete(user=user)

    @staticmethod
    def get_dependentes_funcionario(funcionario: Funcionario) -> list:
        """Retorna todos os dependentes de um funcionario."""
        return list(Dependente.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        ).order_by('nome_completo'))

    @staticmethod
    def get_dependentes_ir(funcionario: Funcionario) -> list:
        """Retorna dependentes inclusos no IR."""
        return list(Dependente.objects.filter(
            funcionario=funcionario,
            incluso_ir=True,
            deleted_at__isnull=True
        ).order_by('nome_completo'))

    @staticmethod
    def get_dependentes_plano_saude(funcionario: Funcionario) -> list:
        """Retorna dependentes inclusos no plano de saude."""
        return list(Dependente.objects.filter(
            funcionario=funcionario,
            incluso_plano_saude=True,
            deleted_at__isnull=True
        ).order_by('nome_completo'))

    @staticmethod
    @transaction.atomic
    def incluir_ir(dependente: Dependente, updated_by=None) -> Dependente:
        """Inclui dependente na declaracao de IR."""
        dependente.incluso_ir = True
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def excluir_ir(dependente: Dependente, updated_by=None) -> Dependente:
        """Exclui dependente da declaracao de IR."""
        dependente.incluso_ir = False
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def incluir_plano_saude(dependente: Dependente, updated_by=None) -> Dependente:
        """Inclui dependente no plano de saude."""
        dependente.incluso_plano_saude = True
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def excluir_plano_saude(dependente: Dependente, updated_by=None) -> Dependente:
        """Exclui dependente do plano de saude."""
        dependente.incluso_plano_saude = False
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    def contar_dependentes(funcionario: Funcionario) -> dict:
        """Retorna contagem de dependentes por categoria."""
        qs = Dependente.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        )

        return {
            'total': qs.count(),
            'ir': qs.filter(incluso_ir=True).count(),
            'plano_saude': qs.filter(incluso_plano_saude=True).count(),
            'com_deficiencia': qs.filter(possui_deficiencia=True).count(),
        }
