import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel
from .enums import StatusExame, ResultadoExame


class ExameRealizado(SoftDeleteModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    aso = models.ForeignKey(
        'sst.ASO',
        on_delete=models.CASCADE,
        related_name='exames_realizados',
        help_text='ASO ao qual este exame pertence'
    )
    
    exame = models.ForeignKey(
        'sst.Exame',
        on_delete=models.PROTECT,
        related_name='realizacoes',
        help_text='Tipo de exame realizado'
    )
    
    status = models.CharField(
        max_length=20,
        choices=StatusExame.choices,
        default=StatusExame.PENDENTE,
        help_text='Status da realização do exame'
    )
    
    resultado = models.CharField(
        max_length=20,
        choices=ResultadoExame.choices,
        blank=True,
        null=True,
        help_text='Resultado do exame (Normal, Alterado)'
    )
    
    data_realizacao = models.DateField(
        blank=True,
        null=True,
        help_text='Data em que o exame foi realizado'
    )
    
    data_validade = models.DateField(
        blank=True,
        null=True,
        help_text='Data de validade deste exame específico'
    )
    
    arquivo = models.FileField(
        upload_to='sst/exames/',
        blank=True,
        null=True,
        help_text='Arquivo PDF/Imagem do exame digitalizado'
    )
    
    observacoes = models.TextField(
        blank=True,
        default='',
        help_text='Observações sobre o exame'
    )

    class Meta:
        db_table = 'exames_realizados'
        verbose_name = 'Exame Realizado'
        verbose_name_plural = 'Exames Realizados'
        indexes = [
            models.Index(fields=['aso', 'status']),
            models.Index(fields=['exame']),
        ]

    def __str__(self):
        return f'{self.exame.nome} ({self.get_status_display()})'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)