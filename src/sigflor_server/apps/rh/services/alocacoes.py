# -*- coding: utf-8 -*-
from typing import Optional
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Alocacao, Funcionario


class AlocacaoService:
    """Service layer para operações com Alocacao."""

    @staticmethod
    @transaction.atomic
    def alocar_funcionario(
        *,
        funcionario: Funcionario,
        projeto,
        data_inicio: date,
        data_fim: Optional[date] = None,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> Alocacao:
        """
        Aloca um funcionário em um projeto.

        Regras:
        - Encerra alocação anterior ativa (se existir)
        - Atualiza o campo projeto no funcionário

        Args:
            funcionario: Funcionário a ser alocado
            projeto: Projeto destino
            data_inicio: Data de início da alocação
            data_fim: Data de fim (opcional, se não informada fica em aberto)
            observacoes: Observações (opcional)
            created_by: Usuário que está realizando a operação

        Returns:
            Alocacao: Instância criada
        """
        # Encerra alocação anterior ativa
        alocacao_ativa = Alocacao.objects.filter(
            funcionario=funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).first()

        if alocacao_ativa:
            alocacao_ativa.data_fim = data_inicio
            alocacao_ativa.updated_by = created_by
            alocacao_ativa.save()

        # Atualiza projeto no funcionário
        funcionario.projeto = projeto
        funcionario.updated_by = created_by
        funcionario.save()

        # Cria nova alocação
        alocacao = Alocacao(
            funcionario=funcionario,
            projeto=projeto,
            data_inicio=data_inicio,
            data_fim=data_fim,
            observacoes=observacoes,
            created_by=created_by,
        )
        alocacao.save()
        return alocacao

    @staticmethod
    @transaction.atomic
    def encerrar_alocacao(
        alocacao: Alocacao,
        data_fim: date,
        updated_by=None
    ) -> Alocacao:
        """
        Encerra uma alocação ativa.

        Args:
            alocacao: Alocação a ser encerrada
            data_fim: Data de encerramento
            updated_by: Usuário que está realizando a operação

        Returns:
            Alocacao: Instância atualizada
        """
        if data_fim < alocacao.data_inicio:
            raise ValidationError(
                'A data de término não pode ser anterior à data de início.'
            )

        alocacao.data_fim = data_fim
        alocacao.updated_by = updated_by
        alocacao.save()

        # Limpa projeto do funcionário se não houver outra alocação ativa
        outra_alocacao = Alocacao.objects.filter(
            funcionario=alocacao.funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).exclude(pk=alocacao.pk).exists()

        if not outra_alocacao:
            alocacao.funcionario.projeto = None
            alocacao.funcionario.updated_by = updated_by
            alocacao.funcionario.save()

        return alocacao

    @staticmethod
    @transaction.atomic
    def update(alocacao: Alocacao, updated_by=None, **kwargs) -> Alocacao:
        """Atualiza uma alocação existente."""
        for attr, value in kwargs.items():
            if hasattr(alocacao, attr):
                setattr(alocacao, attr, value)

        alocacao.updated_by = updated_by
        alocacao.save()
        return alocacao

    @staticmethod
    @transaction.atomic
    def delete(alocacao: Alocacao, user=None) -> None:
        """Soft delete de uma alocação."""
        alocacao.delete(user=user)

    # ========================================================================
    # Consultas
    # ========================================================================

    @staticmethod
    def get_alocacao_ativa(funcionario: Funcionario) -> Optional[Alocacao]:
        """Retorna a alocação ativa do funcionário (se houver)."""
        return Alocacao.objects.filter(
            funcionario=funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).select_related('projeto').first()

    @staticmethod
    def get_historico_funcionario(funcionario: Funcionario) -> list:
        """Retorna histórico de alocações do funcionário."""
        return list(Alocacao.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        ).select_related('projeto').order_by('-data_inicio'))

    @staticmethod
    def get_alocacoes_projeto(projeto, apenas_ativas: bool = True) -> list:
        """Retorna alocações de um projeto."""
        qs = Alocacao.objects.filter(
            projeto=projeto,
            deleted_at__isnull=True
        ).select_related('funcionario', 'funcionario__pessoa_fisica')

        if apenas_ativas:
            qs = qs.filter(data_fim__isnull=True)

        return list(qs.order_by('funcionario__pessoa_fisica__nome_completo'))

    @staticmethod
    def get_funcionarios_projeto(projeto) -> list:
        """Retorna funcionários atualmente alocados em um projeto."""
        from ..models import Funcionario
        alocacoes = Alocacao.objects.filter(
            projeto=projeto,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).values_list('funcionario_id', flat=True)

        return list(Funcionario.objects.filter(
            id__in=alocacoes,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica', 'cargo').order_by(
            'pessoa_fisica__nome_completo'
        ))

    @staticmethod
    def contar_funcionarios_projeto(projeto) -> int:
        """Retorna quantidade de funcionários alocados em um projeto."""
        return Alocacao.objects.filter(
            projeto=projeto,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).count()
