# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q

from apps.comum.models.base import SoftDeleteModel
from .enums import TipoEquipe


class Equipe(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nome único da equipe'
    )

    tipo_equipe = models.CharField(
        max_length=20,
        choices=TipoEquipe.choices,
        help_text='Tipo de equipe (Manual ou Mecanizada)'
    )

    projeto = models.ForeignKey(
        'comum.Projeto',
        on_delete=models.PROTECT,
        related_name='equipes',
        help_text='Projeto ao qual a equipe está alocada'
    )

    lider = models.OneToOneField(
        'rh.Funcionario',
        on_delete=models.PROTECT,
        related_name='equipe_liderada',
        help_text='Líder da equipe'
    )

    coordenador = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.PROTECT,
        related_name='equipes_coordenadas',
        help_text='Coordenador da equipe'
    )

    ativa = models.BooleanField(
        default=True,
        help_text='Indica se a equipe está ativa e operacional'
    )

    observacoes = models.TextField(
        blank=True, 
        default='',
        help_text='Observações'
    )

    class Meta:
        db_table = 'equipes'
        verbose_name = 'Equipe'
        verbose_name_plural = 'Equipes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['projeto', 'ativa', 'nome']),
            models.Index(fields=['coordenador']),
        ]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def membros_count(self):
        return self.membros.filter(
            data_saida__isnull=True,
            deleted_at__isnull=True
        ).count()

    @property
    def projeto_nome(self):
        return self.projeto.descricao if self.projeto else None

    @property
    def lider_nome(self):
        return self.lider.nome if self.lider else None

    @property
    def coordenador_nome(self):
        return self.coordenador.nome if self.coordenador else None


class EquipeFuncionario(SoftDeleteModel):
    """
    Tabela de relacionamento N:M entre Equipe e Funcionário.
    Registra o histórico de participação de funcionários em equipes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE,
        related_name='membros',
        help_text='Equipe'
    )

    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.CASCADE,
        related_name='alocacoes_equipe',
        help_text='Funcionário'
    )

    data_entrada = models.DateField(
        help_text='Data de entrada do funcionário na equipe'
    )

    data_saida = models.DateField(
        null=True,
        blank=True,
        help_text='Data de saída do funcionário da equipe'
    )

    class Meta:
        db_table = 'equipes_funcionarios'
        verbose_name = 'Membro de Equipe'
        verbose_name_plural = 'Membros de Equipe'
        indexes = [
            models.Index(fields=['equipe', 'data_saida']),
            models.Index(fields=['funcionario', 'data_saida']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['equipe', 'funcionario', 'data_entrada'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_equipe_funcionario_data_entrada'
            ),
        ]

    def __str__(self):
        return f'{self.funcionario.nome} em {self.equipe.nome}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_ativo(self):
        return self.data_saida is None and self.deleted_at is None
