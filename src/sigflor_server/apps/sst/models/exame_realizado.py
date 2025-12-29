# -*- coding: utf-8 -*-
import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel
from .enums import Resultado


class ExameRealizado(SoftDeleteModel):
    """
    Registra a realização de um exame por um funcionário.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aso = models.ForeignKey(
        'sst.Aso',
        on_delete=models.CASCADE,
        related_name='exames_realizados',
        help_text='ASO ao qual este exame está vinculado'
    )
    exame = models.ForeignKey(
        'sst.Exame',
        on_delete=models.PROTECT,
        related_name='exames_realizados',
        help_text='Exame que foi realizado'
    )
    data_realizacao = models.DateField(
        help_text='Data em que o exame foi realizado'
    )
    data_vencimento = models.DateField(
        help_text='Data de vencimento do exame'
    )
    resultado = models.CharField(
        max_length=30,
        choices=Resultado.choices,
        blank=True,
        null=True,
        help_text='Resultado do exame (Apto, Inapto, Apto com Restrições)'
    )
    observacoes = models.TextField(
        blank=True,
        default='',
        help_text='Observações adicionais sobre o resultado do exame'
    )
    documento_exame_pdf = models.ForeignKey(
        'comum.Documento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exames_realizados_vinculados',
        help_text='PDF digitalizado do laudo do exame'
    )

    class Meta:
        db_table = 'exames_realizados'
        verbose_name = 'Exame Realizado'
        verbose_name_plural = 'Exames Realizados'
        ordering = ['-data_realizacao', 'exame__nome']
        indexes = [
            models.Index(fields=['aso', 'exame']),
            models.Index(fields=['data_realizacao']),
        ]

    def __str__(self):
        return f'{self.aso.funcionario.nome_completo} - {self.exame.nome}'