# -*- coding: utf-8 -*-
import uuid
from django.db import models

from .base import SoftDeleteModel
from ..validators import validar_cnpj


class SituacaoCadastral(models.TextChoices):
    """Situação cadastral na Receita Federal."""
    ATIVA = 'ativa', 'Ativa'
    SUSPENSA = 'suspensa', 'Suspensa'
    INAPTA = 'inapta', 'Inapta'
    BAIXADA = 'baixada', 'Baixada'
    NULA = 'nula', 'Nula'


class PessoaJuridica(SoftDeleteModel):
    """
    Cadastro técnico e centralizado de pessoas jurídicas.
    Não é criado diretamente pelo usuário - apenas via módulos dependentes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[validar_cnpj],
        help_text="CNPJ com 14 dígitos (apenas números)"
    )
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    data_abertura = models.DateField(blank=True, null=True)
    situacao_cadastral = models.CharField(
        max_length=20,
        choices=SituacaoCadastral.choices,
        default=SituacaoCadastral.ATIVA,
        blank=True,
        null=True
    )
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'pessoa_juridica'
        verbose_name = 'Pessoa Juridica'
        verbose_name_plural = 'Pessoas Juridicas'
        indexes = [
            models.Index(fields=['cnpj']),
            models.Index(fields=['razao_social']),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.cnpj:
            self.cnpj = ''.join(filter(str.isdigit, self.cnpj))
            validar_cnpj(self.cnpj)
        if self.razao_social:
            self.razao_social = self.razao_social.strip().title()
        if self.nome_fantasia:
            self.nome_fantasia = self.nome_fantasia.strip().title()

    def __str__(self):
        return f'{self.razao_social} ({self.cnpj_formatado})'

    @property
    def cnpj_formatado(self):
        if self.cnpj and len(self.cnpj) == 14:
            return f"{self.cnpj[:2]}.{self.cnpj[2:5]}.{self.cnpj[5:8]}/{self.cnpj[8:12]}-{self.cnpj[12:]}"
        return self.cnpj
