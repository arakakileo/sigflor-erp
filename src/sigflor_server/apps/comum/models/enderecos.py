import uuid
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel
from ..validators import EnderecoValidator
from .enums import UF, TipoEndereco


class Endereco(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=20, blank=True, default='')
    complemento = models.CharField(max_length=100, blank=True, default='')
    bairro = models.CharField(max_length=100, blank=True, default='')
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UF.choices)
    cep = models.CharField(max_length=8, help_text='Armazenado sem máscara, apenas dígitos')
    pais = models.CharField(max_length=50, default='Brasil')

    class Meta:
        db_table = 'enderecos'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        indexes = [
            models.Index(fields=['cep']),
            models.Index(fields=['cidade', 'estado']),
        ]

    def clean(self):
        super().clean()
        EnderecoValidator.normalizar(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        partes = [self.logradouro, self.numero, self.bairro, f'{self.cidade}/{self.estado}', self.cep]
        return ' - '.join([p for p in partes if p])

    @property
    def cep_formatado(self):
        if self.cep and len(self.cep) == 8:
            return f"{self.cep[:5]}-{self.cep[5:]}"
        return self.cep

    @property
    def endereco_completo(self) -> str:
        partes = [self.logradouro]
        if self.numero:
            partes.append(f"nº {self.numero}")
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(self.bairro)
        partes.append(f"{self.cidade}/{self.estado}")
        partes.append(f"CEP {self.cep_formatado}")
        return ', '.join(partes)


class PessoaFisicaEndereco(SoftDeleteModel):

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='enderecos_vinculados'
    )
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_fisica'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoEndereco.choices,
        default=TipoEndereco.RESIDENCIAL,
        help_text='Tipo de endereço (residencial, comercial, etc.)'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o endereço principal deste tipo para esta pessoa'
    )

    class Meta:
        db_table = 'pessoas_fisicas_enderecos'
        verbose_name = 'Endereço de Pessoa Física'
        verbose_name_plural = 'Endereços de Pessoas Físicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_fisica', 'endereco'],
                name='uniq_pf_endereco'
            ),

            models.UniqueConstraint(
                fields=['pessoa_fisica', 'tipo'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pf_endereco_principal_por_tipo'
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_fisica} - {self.get_tipo_display()} - {self.endereco}"


class PessoaJuridicaEndereco(SoftDeleteModel):

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    pessoa_juridica = models.ForeignKey(
        'comum.PessoaJuridica',
        on_delete=models.CASCADE,
        related_name='enderecos_vinculados'
    )
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_juridica'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoEndereco.choices,
        default=TipoEndereco.COMERCIAL,
        help_text='Tipo de endereço (comercial, correspondência, etc.)'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o endereço principal deste tipo para esta pessoa jurídica'
    )

    class Meta:
        db_table = 'pessoas_juridicas_enderecos'
        verbose_name = 'Endereço de Pessoa Jurídica'
        verbose_name_plural = 'Endereços de Pessoas Jurídicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica', 'endereco'],
                name='uniq_pj_endereco'
            ),
            models.UniqueConstraint(
                fields=['pessoa_juridica', 'tipo'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pj_endereco_principal_por_tipo'
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_juridica} - {self.get_tipo_display()} - {self.endereco}"


class FilialEndereco(SoftDeleteModel):

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    filial = models.ForeignKey(
        'comum.Filial',
        on_delete=models.CASCADE,
        related_name='enderecos_vinculados'
    )
    endereco = models.ForeignKey(
        Endereco,
        on_delete=models.CASCADE,
        related_name='vinculos_filial'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoEndereco.choices,
        default=TipoEndereco.COMERCIAL,
        help_text='Tipo de endereço (sede, correspondência, etc.)'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o endereço principal deste tipo para esta filial'
    )

    class Meta:
        db_table = 'filiais_enderecos'
        verbose_name = 'Endereço de Filial'
        verbose_name_plural = 'Endereços de Filiais'
        constraints = [
            models.UniqueConstraint(
                fields=['filial', 'endereco'],
                name='uniq_filial_endereco'
            ),
            models.UniqueConstraint(
                fields=['filial', 'tipo'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_filial_endereco_principal_por_tipo'
            ),
        ]

    def __str__(self):
        return f"{self.filial} - {self.get_tipo_display()} - {self.endereco}"
