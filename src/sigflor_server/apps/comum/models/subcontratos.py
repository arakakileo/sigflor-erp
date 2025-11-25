# -*- coding: utf-8 -*-
import uuid
import secrets
import string
from django.db import models

from .base import SoftDeleteModel


class SubContrato(SoftDeleteModel):
    """
    Cadastro de subcontratos entre uma Filial e um Contrato.
    Representa a alocacao de recursos e custos em uma filial especifica.
    E a entidade central para vinculacao de funcionarios, custos, patrimonios, etc.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    numero = models.CharField(
        max_length=20,
        unique=True,
        help_text='Numero do subcontrato (gerado automaticamente)'
    )

    # Vinculos
    filial = models.ForeignKey(
        'comum.Filial',
        on_delete=models.PROTECT,
        related_name='subcontratos',
        help_text='Filial do subcontrato'
    )
    contrato = models.ForeignKey(
        'comum.Contrato',
        on_delete=models.PROTECT,
        related_name='subcontratos',
        help_text='Contrato principal'
    )

    descricao = models.TextField(
        blank=True,
        null=True,
        help_text='Descricao do subcontrato'
    )
    data_inicio = models.DateField(
        help_text='Data de inicio do subcontrato'
    )
    data_fim = models.DateField(
        blank=True,
        null=True,
        help_text='Data de fim do subcontrato'
    )
    ativo = models.BooleanField(
        default=True,
        help_text='Indica se o subcontrato esta ativo'
    )
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'subcontratos'
        verbose_name = 'SubContrato'
        verbose_name_plural = 'SubContratos'
        ordering = ['-data_inicio', 'numero']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['ativo']),
            models.Index(fields=['data_inicio']),
            models.Index(fields=['filial']),
            models.Index(fields=['contrato']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['numero'],
                name='unique_numero_subcontrato'
            ),
        ]

    def __str__(self):
        return f'{self.numero} - {self.filial.nome}'

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._gerar_numero()
        self.full_clean()
        return super().save(*args, **kwargs)

    def _gerar_numero(self):
        """Gera numero unico aleatorio para o subcontrato."""
        while True:
            # Formato: SC + 8 caracteres alfanumericos
            chars = string.ascii_uppercase + string.digits
            numero = 'SC' + ''.join(secrets.choice(chars) for _ in range(8))
            if not SubContrato.objects.filter(numero=numero).exists():
                return numero

    @property
    def is_vigente(self):
        """Verifica se o subcontrato esta vigente."""
        from django.utils import timezone
        hoje = timezone.now().date()
        if not self.ativo:
            return False
        if self.data_fim and self.data_fim < hoje:
            return False
        return self.data_inicio <= hoje

    @property
    def filial_nome(self):
        """Retorna o nome da filial."""
        return self.filial.nome if self.filial else None

    @property
    def contrato_numero(self):
        """Retorna o numero do contrato."""
        return self.contrato.numero_interno if self.contrato else None

    @property
    def contratante_nome(self):
        """Retorna o nome do contratante via contrato."""
        return self.contrato.contratante_nome if self.contrato else None

    @property
    def empresa_nome(self):
        """Retorna o nome da empresa via contrato."""
        return self.contrato.empresa_nome if self.contrato else None
