# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericRelation

from .base import SoftDeleteModel
from ..validators import validar_cpf


class PessoaFisica(SoftDeleteModel):
    """
    Cadastro tecnico de pessoas fisicas.
    Nao e criado diretamente pelo usuario - apenas via modulos dependentes.
    """

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMININO = 'F', 'Feminino'
        OUTRO = 'O', 'Outro'

    class EstadoCivil(models.TextChoices):
        SOLTEIRO = 'solteiro', 'Solteiro(a)'
        CASADO = 'casado', 'Casado(a)'
        DIVORCIADO = 'divorciado', 'Divorciado(a)'
        VIUVO = 'viuvo', 'Viuvo(a)'
        SEPARADO = 'separado', 'Separado(a)'
        UNIAO_ESTAVEL = 'uniao_estavel', 'Uniao Estavel'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=11,
        unique=True,
        validators=[validar_cpf],
        help_text="CPF com 11 digitos (apenas numeros)"
    )
    rg = models.CharField(max_length=20, blank=True, null=True)
    orgao_emissor = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        blank=True,
        null=True
    )
    estado_civil = models.CharField(
        max_length=20,
        choices=EstadoCivil.choices,
        blank=True,
        null=True
    )
    nacionalidade = models.CharField(max_length=100, blank=True, null=True, default='Brasileira')
    naturalidade = models.CharField(max_length=100, blank=True, null=True)

    # Deficiencia
    possui_deficiencia = models.BooleanField(
        default=False,
        help_text='Indica se a pessoa possui alguma deficiencia'
    )

    observacoes = models.TextField(blank=True, null=True)

    # GenericRelations
    enderecos = GenericRelation(
        'comum.Endereco',
        related_query_name='pessoa_fisica'
    )
    contatos = GenericRelation(
        'comum.Contato',
        related_query_name='pessoa_fisica'
    )
    documentos = GenericRelation(
        'comum.Documento',
        related_query_name='pessoa_fisica'
    )
    anexos = GenericRelation(
        'comum.Anexo',
        related_query_name='pessoa_fisica'
    )

    class Meta:
        db_table = 'pessoa_fisica'
        verbose_name = 'Pessoa Fisica'
        verbose_name_plural = 'Pessoas Fisicas'
        indexes = [
            models.Index(fields=['cpf']),
            models.Index(fields=['nome_completo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['cpf'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_cpf_pessoa_fisica_vivo',
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
            validar_cpf(self.cpf)
        if self.nome_completo:
            self.nome_completo = self.nome_completo.strip().title()

    def __str__(self):
        return f'{self.nome_completo} ({self.cpf_formatado})'

    @property
    def cpf_formatado(self):
        if self.cpf and len(self.cpf) == 11:
            return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
        return self.cpf
