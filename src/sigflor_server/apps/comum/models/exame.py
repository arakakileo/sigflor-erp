from django.db import models
from apps.comum.models.base import SoftDeleteModel, AuditModel


class Exame(SoftDeleteModel, AuditModel):
    """
    Representa um exame de saúde ocupacional (entidade mestre).
    Exemplos: Acuidade Visual, Audiometria, Hemograma, etc.
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Exame")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do Exame")

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
        ]

    def __str__(self):
        return self.nome
