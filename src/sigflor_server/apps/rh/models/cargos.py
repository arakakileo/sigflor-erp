# -*- coding: utf-8 -*-
import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel
from .enums import NivelCargo, RiscoPadrao


class Cargo(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nome do cargo'
    )
    
    cbo = models.CharField(
        max_length=10,
        blank=True, 
        default='',
        help_text='Código CBO (Classificação Brasileira de Ocupações)'
    )

    salario_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Salário base do cargo'
    )

    descricao = models.TextField(
        blank=True, 
        default='',
        help_text='Descrição das atribuições do cargo'
    )

    nivel = models.CharField(
        max_length=20,
        choices=NivelCargo.choices,
        help_text='Nível hierárquico do cargo'
    )

    risco_fisico = models.CharField(
        max_length=255,
        default=RiscoPadrao.FISICO,
        help_text='Descrição do risco físico ou indicação de ausência.'
    )

    risco_biologico = models.CharField(
        max_length=255,
        default=RiscoPadrao.BIOLOGICO,
        help_text='Descrição do risco biológico ou indicação de ausência.'
    )

    risco_quimico = models.CharField(
        max_length=255,
        default=RiscoPadrao.QUIMICO,
        help_text='Descrição do risco químico ou indicação de ausência.'
    )

    risco_ergonomico = models.CharField(
        max_length=255,
        default=RiscoPadrao.ERGONOMICO,
        help_text='Descrição do risco ergonômico ou indicação de ausência.'
    )

    risco_acidente = models.CharField(
        max_length=255,
        default=RiscoPadrao.ACIDENTE,
        help_text='Descrição do risco de acidente ou indicação de ausência.'
    )

    ativo = models.BooleanField(
        default=True,
        help_text='Indica se o cargo está ativo'
    )

    class Meta:
        db_table = 'cargos'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['ativo', 'nome']),
            models.Index(fields=['cbo']),
        ]

    def __str__(self):
        cbo_str = f' (CBO: {self.cbo})' if self.cbo else ''
        return f'{self.nome}{cbo_str}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def funcionarios_count(self):
        """Retorna a quantidade de funcionários neste cargo."""
        return self.funcionarios.filter(deleted_at__isnull=True).count()

    @property
    def tem_risco(self):
        return any([
            self.risco_fisico != RiscoPadrao.FISICO,
            self.risco_biologico != RiscoPadrao.BIOLOGICO,
            self.risco_quimico != RiscoPadrao.QUIMICO,
            self.risco_ergonomico != RiscoPadrao.ERGONOMICO,
            self.risco_acidente != RiscoPadrao.ACIDENTE
        ])
