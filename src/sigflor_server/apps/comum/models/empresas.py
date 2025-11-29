import uuid
from django.db import models

from .base import SoftDeleteModel


class Empresa(SoftDeleteModel):
    """
    Representa as empresas pertencentes ao grupo econômico da organização.
    É uma especialização de PessoaJuridica.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa_juridica = models.OneToOneField(
        'comum.PessoaJuridica',
        on_delete=models.PROTECT,
        related_name='empresa',
        help_text="Dados jurídicos associados"
    )
    descricao = models.TextField(blank=True, null=True, help_text="Observações internas")
    ativa = models.BooleanField(default=True, help_text="Indica se a empresa está ativa")


    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica'],
                name='uniq_empresa_pessoa_juridica'
            ),
        ]

    def __str__(self):
        return str(self.pessoa_juridica)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def razao_social(self):
        return self.pessoa_juridica.razao_social

    @property
    def cnpj(self):
        return self.pessoa_juridica.cnpj

    @property
    def cnpj_formatado(self):
        return self.pessoa_juridica.cnpj_formatado
