# -*- coding: utf-8 -*-
import uuid
from django.db import models

from .base import SoftDeleteModel


class Contrato(SoftDeleteModel):
    """
    Cadastro de contratos entre uma Cliente e uma Empresa.
    Representa acordos comerciais formais entre as partes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    numero_interno = models.CharField(
        max_length=50,
        unique=True,
        help_text='Numero interno do contrato (unico)'
    )
    numero_externo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text='Numero externo do contrato (unico)'
    )

    # Vinculos
    cliente = models.ForeignKey(
        'comum.Cliente',
        on_delete=models.PROTECT,
        related_name='contratos',
        help_text='Cliente do contrato'
    )
    empresa = models.ForeignKey(
        'comum.Empresa',
        on_delete=models.PROTECT,
        related_name='contratos',
        help_text='Empresa do grupo contratada'
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        help_text='Descricao do contrato'
    )
    data_inicio = models.DateField(
        help_text='Data de inicio do contrato'
    )
    data_fim = models.DateField(
        blank=True,
        null=True,
        help_text='Data de fim do contrato'
    )
    ativo = models.BooleanField(
        default=True,
        help_text='Indica se o contrato esta ativo'
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Valor do contrato'
    )
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'contratos'
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-data_inicio', 'numero_interno']
        indexes = [
            models.Index(fields=['numero_interno']),
            models.Index(fields=['numero_externo']),
            models.Index(fields=['ativo']),
            models.Index(fields=['data_inicio']),
            models.Index(fields=['cliente']),
            models.Index(fields=['empresa']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['numero_interno'],
                name='unique_numero_interno_contrato'
            ),
            models.UniqueConstraint(
                fields=['numero_externo'],
                condition=models.Q(numero_externo__isnull=False),
                name='unique_numero_externo_contrato'
            ),
        ]

    def __str__(self):
        return f'{self.numero_interno} - {self.cliente}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_vigente(self):
        """Verifica se o contrato esta vigente."""
        from django.utils import timezone
        hoje = timezone.now().date()
        if not self.ativo:
            return False
        if self.data_fim and self.data_fim < hoje:
            return False
        return self.data_inicio <= hoje

    @property
    def cliente_nome(self):
        """Retorna o nome do cliente."""
        return self.cliente.pessoa_juridica.razao_social if self.cliente else None

    @property
    def empresa_nome(self):
        """Retorna o nome da empresa."""
        return self.empresa.pessoa_juridica.razao_social if self.empresa else None
