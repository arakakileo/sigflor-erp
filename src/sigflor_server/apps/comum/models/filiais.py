# -*- coding: utf-8 -*-
import uuid
from django.db import models

from .base import SoftDeleteModel


class Filial(SoftDeleteModel):
    """
    Cadastro de filiais da empresa.
    Representa unidades operacionais vinculadas a uma empresa do grupo.
    """

    class Status(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        INATIVA = 'inativa', 'Inativa'
        SUSPENSA = 'suspensa', 'Suspensa'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=200,
        help_text='Nome da filial'
    )
    codigo_interno = models.CharField(
        max_length=50,
        unique=True,
        help_text='Codigo interno da filial'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVA,
        help_text='Status da filial'
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text='Descricao da filial'
    )

    # Vinculo com empresa do grupo (opcional)
    empresa = models.ForeignKey(
        'comum.Empresa',
        on_delete=models.PROTECT,
        related_name='filiais',
        blank=True,
        null=True,
        help_text='Empresa do grupo a qual a filial pertence'
    )

    # Relacionamento com Enderecos via tabela de vínculo explícita (FilialEndereco)
    enderecos = models.ManyToManyField(
        'comum.Endereco',
        through='comum.FilialEndereco',
        related_name='filiais',
        help_text='Endereços da filial'
    )
    contatos = models.ManyToManyField(
        'comum.Contato',
        through='comum.FilialContato',
        related_name='filiais',
        help_text='Contatos da filial'
    )

    class Meta:
        db_table = 'filiais'
        verbose_name = 'Filial'
        verbose_name_plural = 'Filiais'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo_interno']),
            models.Index(fields=['status']),
            models.Index(fields=['nome']),
        ]

    def __str__(self):
        return f'{self.nome} ({self.codigo_interno})'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_ativa(self):
        """Verifica se a filial esta ativa."""
        return self.status == self.Status.ATIVA and self.deleted_at is None

    @property
    def empresa_nome(self):
        """Retorna o nome da empresa."""
        if self.empresa and self.empresa.pessoa_juridica:
            return self.empresa.pessoa_juridica.razao_social
        return None
