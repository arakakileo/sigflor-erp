# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField

from .base import SoftDeleteModel
from ..validators import validar_cnpj


class PessoaJuridica(SoftDeleteModel):
    """
    Cadastro tecnico e centralizado de pessoas juridicas.
    Nao e criado diretamente pelo usuario - apenas via modulos dependentes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True)
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        validators=[validar_cnpj],
        help_text="CNPJ com 14 digitos (apenas numeros)"
    )
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    data_abertura = models.DateField(blank=True, null=True)
    situacao_cadastral = models.CharField(
        max_length=20,
        choices=SituacaoCadastral.choices,
        default=SituacaoCadastral.ATIVA
    )
    observacoes = models.TextField(blank=True, null=True)

    # GenericRelations
    enderecos = GenericRelation(
        'comum.Endereco',
        related_query_name='pessoa_juridica'
    )
    contatos = models.ManyToManyField(
        'comum.Contato',
        through='comum.PessoaJuridicaContato',
        related_name='pessoas_juridicas',
        help_text='Contatos da pessoa jurídica'
    )
    documentos = GenericRelation(
        'comum.Documento',
        related_query_name='pessoa_juridica'
    )

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
