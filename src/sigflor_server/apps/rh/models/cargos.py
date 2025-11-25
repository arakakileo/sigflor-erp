# -*- coding: utf-8 -*-
import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel


class Cargo(SoftDeleteModel):
    """
    Cadastro de cargos da empresa.
    Define a posicao, salario base e classificacao CBO.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nome do cargo'
    )
    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Salario base do cargo'
    )
    cbo = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Codigo CBO (Classificacao Brasileira de Ocupacoes)'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text='Descricao das atribuicoes do cargo'
    )
    nivel = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Nivel hierarquico (Junior, Pleno, Senior, etc.)'
    )
    ativo = models.BooleanField(
        default=True,
        help_text='Indica se o cargo esta ativo'
    )

    class Meta:
        db_table = 'cargos'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cbo']),
            models.Index(fields=['ativo']),
        ]

    def __str__(self):
        cbo_str = f' (CBO: {self.cbo})' if self.cbo else ''
        return f'{self.nome}{cbo_str}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def funcionarios_count(self):
        """Retorna a quantidade de funcionarios neste cargo."""
        return self.funcionarios.filter(deleted_at__isnull=True).count()
