import uuid
from django.db import models

from .base import SoftDeleteModel


class Contratante(SoftDeleteModel):
    """
    Representa empresas responsáveis pela contratação dos serviços da organização.
    É uma especialização de PessoaJuridica.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pessoa_juridica = models.OneToOneField(
        'comum.PessoaJuridica',
        on_delete=models.PROTECT,
        related_name='contratante',
        help_text="Dados jurídicos da empresa contratante"
    )
    descricao = models.TextField(blank=True, null=True, help_text="Observações complementares")
    ativo = models.BooleanField(default=True, help_text="Indica se o contratante está ativo")

    class Meta:
        db_table = 'contratantes'
        verbose_name = 'Contratante'
        verbose_name_plural = 'Contratantes'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica'],
                name='uniq_contratante_pessoa_juridica'
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
    def nome_fantasia(self):
        return self.pessoa_juridica.nome_fantasia

    @property
    def cnpj(self):
        return self.pessoa_juridica.cnpj

    @property
    def cnpj_formatado(self):
        return self.pessoa_juridica.cnpj_formatado
