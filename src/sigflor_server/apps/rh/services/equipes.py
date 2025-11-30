# -*- coding: utf-8 -*-
from typing import Optional
from datetime import date
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Equipe, EquipeFuncionario, Funcionario


class EquipeService:
    """Service layer para operações com Equipe e EquipeFuncionario."""

    # ========================================================================
    # Operações de Equipe
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def criar_equipe(
        *,
        nome: str,
        tipo_equipe: str,
        projeto,
        lider: Optional[Funcionario] = None,
        coordenador: Optional[Funcionario] = None,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> Equipe:
        """
        Cria uma nova equipe.

        Regras:
        - Nome deve ser único
        - Se líder fornecido, valida que ele não seja líder de outra equipe

        Args:
            nome: Nome único da equipe
            tipo_equipe: Tipo (MANUAL ou MECANIZADA)
            projeto: Projeto ao qual a equipe está alocada
            lider: Funcionário líder (opcional)
            coordenador: Funcionário coordenador (opcional)
            observacoes: Observações (opcional)
            created_by: Usuário que está criando

        Returns:
            Equipe: Instância criada
        """
        # Valida líder
        if lider:
            equipe_existente = Equipe.objects.filter(
                lider=lider,
                deleted_at__isnull=True
            ).first()
            if equipe_existente:
                raise ValidationError(
                    f'O funcionário {lider.nome} já é líder da equipe "{equipe_existente.nome}".'
                )

        equipe = Equipe(
            nome=nome,
            tipo_equipe=tipo_equipe,
            projeto=projeto,
            lider=lider,
            coordenador=coordenador,
            observacoes=observacoes,
            created_by=created_by,
        )
        equipe.save()
        return equipe

    @staticmethod
    @transaction.atomic
    def update(equipe: Equipe, updated_by=None, **kwargs) -> Equipe:
        """Atualiza uma equipe existente."""
        # Valida novo líder se fornecido
        novo_lider = kwargs.get('lider')
        if novo_lider and novo_lider != equipe.lider:
            equipe_existente = Equipe.objects.filter(
                lider=novo_lider,
                deleted_at__isnull=True
            ).exclude(pk=equipe.pk).first()
            if equipe_existente:
                raise ValidationError(
                    f'O funcionário {novo_lider.nome} já é líder da equipe "{equipe_existente.nome}".'
                )

        for attr, value in kwargs.items():
            if hasattr(equipe, attr):
                setattr(equipe, attr, value)

        equipe.updated_by = updated_by
        equipe.save()
        return equipe

    @staticmethod
    @transaction.atomic
    def delete(equipe: Equipe, user=None) -> None:
        """Soft delete de uma equipe."""
        equipe.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(equipe: Equipe, updated_by=None) -> Equipe:
        """Ativa uma equipe."""
        equipe.ativa = True
        equipe.updated_by = updated_by
        equipe.save()
        return equipe

    @staticmethod
    @transaction.atomic
    def desativar(equipe: Equipe, updated_by=None) -> Equipe:
        """Desativa uma equipe."""
        equipe.ativa = False
        equipe.updated_by = updated_by
        equipe.save()
        return equipe

    @staticmethod
    @transaction.atomic
    def alterar_lider(
        equipe: Equipe,
        novo_lider: Optional[Funcionario],
        updated_by=None
    ) -> Equipe:
        """Altera o líder da equipe."""
        if novo_lider:
            equipe_existente = Equipe.objects.filter(
                lider=novo_lider,
                deleted_at__isnull=True
            ).exclude(pk=equipe.pk).first()
            if equipe_existente:
                raise ValidationError(
                    f'O funcionário {novo_lider.nome} já é líder da equipe "{equipe_existente.nome}".'
                )

        equipe.lider = novo_lider
        equipe.updated_by = updated_by
        equipe.save()
        return equipe

    # ========================================================================
    # Operações de EquipeFuncionario (Membros)
    # ========================================================================

    @staticmethod
    @transaction.atomic
    def adicionar_membro(
        *,
        equipe: Equipe,
        funcionario: Funcionario,
        data_entrada: date,
        created_by=None,
    ) -> EquipeFuncionario:
        """
        Adiciona um funcionário a uma equipe.

        Regras:
        - Se o funcionário já estiver em outra equipe ativa, encerra a alocação anterior
        - A data de entrada não pode ser futura

        Args:
            equipe: Equipe onde o funcionário será adicionado
            funcionario: Funcionário a ser adicionado
            data_entrada: Data de entrada na equipe
            created_by: Usuário que está realizando a operação

        Returns:
            EquipeFuncionario: Registro de alocação criado
        """
        # Encerra alocação anterior ativa (se existir)
        alocacao_ativa = EquipeFuncionario.objects.filter(
            funcionario=funcionario,
            data_saida__isnull=True,
            deleted_at__isnull=True
        ).first()

        if alocacao_ativa:
            alocacao_ativa.data_saida = data_entrada
            alocacao_ativa.updated_by = created_by
            alocacao_ativa.save()

        # Cria nova alocação
        equipe_funcionario = EquipeFuncionario(
            equipe=equipe,
            funcionario=funcionario,
            data_entrada=data_entrada,
            created_by=created_by,
        )
        equipe_funcionario.save()
        return equipe_funcionario

    @staticmethod
    @transaction.atomic
    def remover_membro(
        *,
        equipe_funcionario: EquipeFuncionario,
        data_saida: date,
        updated_by=None,
    ) -> EquipeFuncionario:
        """
        Remove um funcionário de uma equipe (encerra a participação).

        Args:
            equipe_funcionario: Registro de alocação
            data_saida: Data de saída
            updated_by: Usuário que está realizando a operação

        Returns:
            EquipeFuncionario: Registro atualizado
        """
        if data_saida < equipe_funcionario.data_entrada:
            raise ValidationError(
                'A data de saída não pode ser anterior à data de entrada.'
            )

        equipe_funcionario.data_saida = data_saida
        equipe_funcionario.updated_by = updated_by
        equipe_funcionario.save()
        return equipe_funcionario

    @staticmethod
    @transaction.atomic
    def transferir_membro(
        *,
        funcionario: Funcionario,
        equipe_destino: Equipe,
        data_transferencia: date,
        updated_by=None,
    ) -> EquipeFuncionario:
        """
        Transfere um funcionário para outra equipe.

        Args:
            funcionario: Funcionário a ser transferido
            equipe_destino: Nova equipe
            data_transferencia: Data da transferência
            updated_by: Usuário que está realizando a operação

        Returns:
            EquipeFuncionario: Nova alocação criada
        """
        return EquipeService.adicionar_membro(
            equipe=equipe_destino,
            funcionario=funcionario,
            data_entrada=data_transferencia,
            created_by=updated_by,
        )

    # ========================================================================
    # Consultas
    # ========================================================================

    @staticmethod
    def get_equipes_ativas() -> list:
        """Retorna lista de equipes ativas."""
        return list(Equipe.objects.filter(
            ativa=True,
            deleted_at__isnull=True
        ).select_related('projeto', 'lider', 'coordenador').order_by('nome'))

    @staticmethod
    def get_equipes_por_projeto(projeto) -> list:
        """Retorna equipes de um projeto."""
        return list(Equipe.objects.filter(
            projeto=projeto,
            deleted_at__isnull=True
        ).select_related('lider', 'coordenador').order_by('nome'))

    @staticmethod
    def get_membros_ativos(equipe: Equipe) -> list:
        """Retorna membros ativos de uma equipe."""
        return list(EquipeFuncionario.objects.filter(
            equipe=equipe,
            data_saida__isnull=True,
            deleted_at__isnull=True
        ).select_related('funcionario', 'funcionario__pessoa_fisica').order_by(
            'funcionario__pessoa_fisica__nome_completo'
        ))

    @staticmethod
    def get_historico_membros(equipe: Equipe) -> list:
        """Retorna histórico completo de membros da equipe."""
        return list(EquipeFuncionario.objects.filter(
            equipe=equipe,
            deleted_at__isnull=True
        ).select_related('funcionario', 'funcionario__pessoa_fisica').order_by(
            '-data_entrada'
        ))

    @staticmethod
    def get_equipe_atual_funcionario(funcionario: Funcionario) -> Optional[Equipe]:
        """Retorna a equipe atual do funcionário (se houver)."""
        alocacao = EquipeFuncionario.objects.filter(
            funcionario=funcionario,
            data_saida__isnull=True,
            deleted_at__isnull=True
        ).select_related('equipe').first()
        return alocacao.equipe if alocacao else None

    @staticmethod
    def get_historico_equipes_funcionario(funcionario: Funcionario) -> list:
        """Retorna histórico de equipes do funcionário."""
        return list(EquipeFuncionario.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        ).select_related('equipe', 'equipe__projeto').order_by('-data_entrada'))
