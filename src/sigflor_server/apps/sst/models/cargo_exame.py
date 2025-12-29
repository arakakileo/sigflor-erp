# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q

from apps.comum.models.base import SoftDeleteModel


class CargoExame(SoftDeleteModel):
    """
    Define quais exames são obrigatórios para cada Cargo.
    Estabelece as regras de saúde ocupacional e requisitos de exames
    para a admissão e manutenção do vínculo empregatício.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cargo = models.ForeignKey(
        'rh.Cargo',
        on_delete=models.CASCADE,
        related_name='exames_obrigatorios',
        help_text='Cargo ao qual esta regra de exame se aplica'
    )
    exame = models.ForeignKey(
        'sst.Exame',
        on_delete=models.CASCADE,
        related_name='cargos_associados',
        help_text='Exame exigido para o cargo'
    )
    periodicidade_meses = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Periodicidade em meses para a realização do exame (se aplicável)'
    )
    observacoes = models.TextField(
        blank=True, 
        default='',
        help_text='Observações adicionais sobre o exame para este cargo'
    )

    class Meta:
        db_table = 'cargos_exames'
        verbose_name = 'Exame de Cargo'
        verbose_name_plural = 'Exames de Cargos'
        ordering = ['cargo', 'exame__nome']
        constraints = [
            models.UniqueConstraint(
                fields=['cargo', 'exame'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_cargo_exame'
            ),
        ]


    def __str__(self):
        return f'{self.cargo.nome} - {self.exame.nome}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def cargo_nome(self):
        return self.cargo.nome if self.cargo else None

    @property
    def exame_nome(self):
        return self.exame.nome if self.exame else None
        