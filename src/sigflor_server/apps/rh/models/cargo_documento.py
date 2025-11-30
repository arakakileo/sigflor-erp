# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q

from apps.comum.models.base import SoftDeleteModel
from apps.comum.models.documentos import Documento


class CargoDocumento(SoftDeleteModel):
    """
    Define quais documentos são obrigatórios para cada Cargo.
    Estabelece as regras de compliance e requisitos documentais
    para a admissão e manutenção do vínculo empregatício.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cargo = models.ForeignKey(
        'rh.Cargo',
        on_delete=models.CASCADE,
        related_name='documentos_obrigatorios',
        help_text='Cargo ao qual esta regra documental se aplica'
    )
    documento_tipo = models.CharField(
        max_length=50,
        choices=Documento.Tipo.choices,
        help_text='Tipo de documento exigido'
    )
    obrigatorio = models.BooleanField(
        default=True,
        help_text='Indica se a posse deste documento é mandatória para o cargo'
    )
    condicional = models.TextField(
        blank=True,
        null=True,
        help_text='Descrição de condições adicionais para a obrigatoriedade'
    )

    class Meta:
        db_table = 'cargos_documentos'
        verbose_name = 'Documento de Cargo'
        verbose_name_plural = 'Documentos de Cargos'
        ordering = ['cargo', 'documento_tipo']
        constraints = [
            models.UniqueConstraint(
                fields=['cargo', 'documento_tipo'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_cargo_documento_tipo'
            ),
        ]

    def __str__(self):
        status = 'Obrigatório' if self.obrigatorio else 'Opcional'
        return f'{self.cargo.nome} - {self.get_documento_tipo_display()} ({status})'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def cargo_nome(self):
        """Retorna o nome do cargo."""
        return self.cargo.nome if self.cargo else None

    @property
    def tipo_display(self):
        """Retorna o display do tipo de documento."""
        return self.get_documento_tipo_display()
