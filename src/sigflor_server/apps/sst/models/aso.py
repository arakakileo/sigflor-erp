import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel
from .enums import Tipo, Status, Resultado


class ASO(SoftDeleteModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.PROTECT,
        related_name='asos',
        help_text='Funcionário ao qual se refere o ASO'
    )
    
    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        help_text='Tipo do ASO (Admissional, Periódico, etc.)'
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTO,
        help_text='Status do processo do ASO'
    )
    
    resultado = models.CharField(
        max_length=30,
        choices=Resultado.choices,
        blank=True,
        null=True,
        help_text='Resultado final do ASO (Apto, Inapto, etc.)'
    )
    
    data_emissao = models.DateField(
        blank=True,
        null=True,
        help_text='Data de emissão do ASO'
    )
    
    validade = models.DateField(
        blank=True,
        null=True,
        help_text='Data de validade do ASO'
    )
    
    medico_coordenador = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text='Nome do médico coordenador do PCMSO'
    )
    
    medico_examinador = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text='Nome do médico que realizou o exame clínico'
    )
    
    observacoes = models.TextField(
        blank=True,
        default='',
        help_text='Observações gerais do ASO'
    )

    class Meta:
        db_table = 'asos'
        verbose_name = 'ASO'
        verbose_name_plural = 'ASOs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['funcionario', 'tipo']),
            models.Index(fields=['status']),
            models.Index(fields=['validade']),
        ]

    def __str__(self):
        return f'ASO {self.get_tipo_display()} - {self.funcionario.nome}'

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)