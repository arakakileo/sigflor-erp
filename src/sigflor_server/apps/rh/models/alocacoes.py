# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q

from apps.comum.models.base import SoftDeleteModel


class Alocacao(SoftDeleteModel):
    """
    Registra o histórico de vinculação de um Funcionário a um Projeto.
    Essencial para controle de custos, apropriação de despesas e
    rastreabilidade da trajetória do funcionário.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.PROTECT,
        related_name='alocacoes',
        help_text='Funcionário alocado'
    )
    projeto = models.ForeignKey(
        'comum.Projeto',
        on_delete=models.PROTECT,
        related_name='alocacoes',
        help_text='Projeto ao qual o funcionário está vinculado'
    )
    data_inicio = models.DateField(
        help_text='Data de início da alocação no projeto'
    )
    data_fim = models.DateField(
        null=True,
        blank=True,
        help_text='Data de término da alocação. Se null, a alocação está ativa.'
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text='Detalhes ou justificativas da alocação'
    )

    class Meta:
        db_table = 'alocacoes'
        verbose_name = 'Alocação'
        verbose_name_plural = 'Alocações'
        ordering = ['-data_inicio']
        indexes = [
            models.Index(fields=['funcionario', 'data_inicio', 'data_fim']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['funcionario', 'projeto', 'data_inicio'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_funcionario_projeto_data_inicio'
            ),
        ]

    def __str__(self):
        status = 'Ativa' if self.is_ativa else 'Encerrada'
        return f'{self.funcionario.nome} em {self.projeto.descricao} ({status})'

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()
        # Valida que data_fim não seja anterior a data_inicio
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': 'A data de término não pode ser anterior à data de início.'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_ativa(self):
        """Indica se a alocação está ativa."""
        return self.data_fim is None and self.deleted_at is None

    @property
    def funcionario_nome(self):
        """Retorna o nome do funcionário."""
        return self.funcionario.nome if self.funcionario else None

    @property
    def projeto_descricao(self):
        """Retorna a descrição do projeto."""
        return self.projeto.descricao if self.projeto else None

    @property
    def duracao_dias(self):
        """Retorna a duração da alocação em dias."""
        from django.utils import timezone
        fim = self.data_fim or timezone.now().date()
        return (fim - self.data_inicio).days
