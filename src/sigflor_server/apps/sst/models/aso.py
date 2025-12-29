# -*- coding: utf-8 -*-
import uuid
from django.db import models


from apps.comum.models.base import SoftDeleteModel
from .enums import Tipo, Status, Resultado


class Aso(SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.PROTECT,
        related_name='aso'
    )
    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTO
    )
    data_solicitacao = models.DateField(auto_now_add=True)
    data_finalizacao = models.DateField(blank=True, null=True)
    resultado = models.CharField(
        max_length=30,
        choices=Resultado.choices,
        blank=True,
        null=True
    )
    observacoes = models.TextField(blank=True, default='')
    documento_aso_pdf = models.ForeignKey(
        'comum.Documento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asos_vinculados',
        help_text='PDF digitalizado do ASO assinado'
    )

    class Meta:
        db_table = 'aso'
        verbose_name = 'Aso'
        verbose_name_plural = 'Aso'
        ordering = ['-data_solicitacao']
        indexes = [
            models.Index(fields=['funcionario', 'status']),
        ]