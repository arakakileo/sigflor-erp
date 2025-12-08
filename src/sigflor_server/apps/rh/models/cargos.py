# -*- coding: utf-8 -*-
import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel
from .enums import NivelCargo


class Cargo(SoftDeleteModel):
    """
    Cadastro de cargos da empresa.
    Define a posição, salário base, classificação CBO e níveis de risco ocupacional.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nome do cargo'
    )
    
    cbo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
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
        null=True,
        help_text='Descrição das atribuições do cargo'
    )

    nivel = models.CharField(
        max_length=20,
        choices=NivelCargo.choices,
        help_text='Nível hierárquico do cargo'
    )

    # Indicadores de risco ocupacional
    risco_fisico = models.BooleanField(
        default=False,
        help_text='Indica exposição a riscos físicos'
    )

    risco_biologico = models.BooleanField(
        default=False,
        help_text='Indica exposição a riscos biológicos'
    )

    risco_quimico = models.BooleanField(
        default=False,
        help_text='Indica exposição a riscos químicos'
    )

    risco_ergonomico = models.BooleanField(
        default=False,
        help_text='Indica exposição a riscos ergonômicos'
    )

    risco_acidente = models.BooleanField(
        default=False,
        help_text='Indica exposição a riscos de acidente'
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
        """Indica se o cargo possui algum tipo de risco."""
        return any([
            self.risco_fisico,
            self.risco_biologico,
            self.risco_quimico,
            self.risco_ergonomico,
            self.risco_acidente
        ])
