# -*- coding: utf-8 -*-
from typing import Optional
from django.db import models, transaction
from django.core.exceptions import ValidationError

from apps.comum.models import PessoaFisica
from apps.comum.services import PessoaFisicaService
from ..models import Funcionario, Dependente


class DependenteService:
    """Service layer para operações com Dependente."""

    @staticmethod
    @transaction.atomic
    def vincular_dependente(
        *,
        funcionario: Funcionario,
        pessoa_fisica_data: dict,
        parentesco: str,
        dependencia_irrf: bool = False,
        created_by=None,
    ) -> Dependente:
        """
        Vincula um dependente a um funcionário.

        Fluxo:
        1. Cria ou recupera PessoaFisica via PessoaFisicaService
        2. Verifica se o dependente já existe para este funcionário
        3. Cria o registro de Dependente
        4. Atualiza flag tem_dependente do funcionário

        Args:
            funcionario: Funcionário titular
            pessoa_fisica_data: Dados da pessoa física do dependente
            parentesco: Grau de parentesco (Dependente.Parentesco)
            dependencia_irrf: Se é dependente para fins de IR
            created_by: Usuário que está realizando a operação

        Returns:
            Dependente: Instância do dependente criado

        Raises:
            ValidationError: Se dados inválidos ou dependente já existe
        """
        # 1. Gerenciamento de PessoaFisica do dependente
        cpf = pessoa_fisica_data.get('cpf')
        if cpf:
            # Tenta buscar pessoa física existente pelo CPF
            cpf_limpo = cpf.replace('.', '').replace('-', '')
            pessoa_fisica = PessoaFisica.objects.filter(
                cpf=cpf_limpo,
                deleted_at__isnull=True
            ).first()

            if pessoa_fisica:
                # Verifica se já é dependente deste funcionário
                if Dependente.objects.filter(
                    funcionario=funcionario,
                    pessoa_fisica=pessoa_fisica,
                    deleted_at__isnull=True
                ).exists():
                    raise ValidationError(
                        'Esta pessoa já está cadastrada como dependente deste funcionário.'
                    )
            else:
                # Cria nova pessoa física
                pessoa_fisica = PessoaFisicaService.create(
                    created_by=created_by,
                    **pessoa_fisica_data
                )
        else:
            # Cria nova pessoa física sem CPF prévio
            pessoa_fisica = PessoaFisicaService.create(
                created_by=created_by,
                **pessoa_fisica_data
            )

        # 2. Criação do Dependente
        dependente = Dependente(
            funcionario=funcionario,
            pessoa_fisica=pessoa_fisica,
            parentesco=parentesco,
            dependencia_irrf=dependencia_irrf,
            created_by=created_by
        )
        dependente.save()  # save() já atualiza tem_dependente

        return dependente

    @staticmethod
    @transaction.atomic
    def update(dependente: Dependente, updated_by=None, **kwargs) -> Dependente:
        """Atualiza um dependente existente."""
        for attr, value in kwargs.items():
            if hasattr(dependente, attr):
                setattr(dependente, attr, value)

        dependente.updated_by = updated_by
        dependente.save()  # save() já atualiza tem_dependente se ativo mudou
        return dependente

    @staticmethod
    @transaction.atomic
    def delete(dependente: Dependente, user=None) -> None:
        """Soft delete de um dependente."""
        dependente.delete(user=user)  # delete() já atualiza tem_dependente

    @staticmethod
    @transaction.atomic
    def desativar_dependente(dependente: Dependente, updated_by=None) -> Dependente:
        """
        Desativa um dependente (soft delete lógico).

        Mantém o registro no sistema mas marca como inativo.
        Atualiza flag tem_dependente do funcionário se necessário.
        """
        dependente.ativo = False
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def reativar_dependente(dependente: Dependente, updated_by=None) -> Dependente:
        """Reativa um dependente previamente desativado."""
        dependente.ativo = True
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    @transaction.atomic
    def atualizar_dependencia_irrf(
        dependente: Dependente,
        dependencia_irrf: bool,
        updated_by=None
    ) -> Dependente:
        """Atualiza status de dependência para IRRF."""
        dependente.dependencia_irrf = dependencia_irrf
        dependente.updated_by = updated_by
        dependente.save()
        return dependente

    @staticmethod
    def get_dependentes_funcionario(
        funcionario: Funcionario,
        apenas_ativos: bool = True
    ) -> list:
        """Retorna todos os dependentes de um funcionário."""
        qs = Dependente.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica')

        if apenas_ativos:
            qs = qs.filter(ativo=True)

        return list(qs.order_by('pessoa_fisica__nome_completo'))

    @staticmethod
    def get_dependentes_irrf(funcionario: Funcionario) -> list:
        """Retorna dependentes inclusos no IRRF."""
        return list(Dependente.objects.filter(
            funcionario=funcionario,
            dependencia_irrf=True,
            ativo=True,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo'))

    @staticmethod
    def contar_dependentes(funcionario: Funcionario) -> dict:
        """Retorna contagem de dependentes por categoria."""
        qs = Dependente.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        )

        return {
            'total': qs.count(),
            'ativos': qs.filter(ativo=True).count(),
            'irrf': qs.filter(dependencia_irrf=True, ativo=True).count(),
            'por_parentesco': dict(
                qs.filter(ativo=True).values_list('parentesco').annotate(
                    count=models.Count('id')
                )
            ),
        }
