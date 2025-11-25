import uuid
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .base import SoftDeleteModel
from ..validators import EnderecoValidator


class Endereco(SoftDeleteModel):
    """
    Entidade genérica de endereços utilizando GenericForeignKey.
    Pode ser vinculada a qualquer entidade do sistema.
    """

    class UF(models.TextChoices):
        AC = 'AC', 'AC'
        AL = 'AL', 'AL'
        AP = 'AP', 'AP'
        AM = 'AM', 'AM'
        BA = 'BA', 'BA'
        CE = 'CE', 'CE'
        DF = 'DF', 'DF'
        ES = 'ES', 'ES'
        GO = 'GO', 'GO'
        MA = 'MA', 'MA'
        MT = 'MT', 'MT'
        MS = 'MS', 'MS'
        MG = 'MG', 'MG'
        PA = 'PA', 'PA'
        PB = 'PB', 'PB'
        PR = 'PR', 'PR'
        PE = 'PE', 'PE'
        PI = 'PI', 'PI'
        RJ = 'RJ', 'RJ'
        RN = 'RN', 'RN'
        RS = 'RS', 'RS'
        RO = 'RO', 'RO'
        RR = 'RR', 'RR'
        SC = 'SC', 'SC'
        SP = 'SP', 'SP'
        SE = 'SE', 'SE'
        TO = 'TO', 'TO'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    logradouro = models.CharField(max_length=200)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, choices=UF.choices)
    cep = models.CharField(max_length=8)
    pais = models.CharField(max_length=50, default='Brasil')

    # GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID como string
    entidade = GenericForeignKey('content_type', 'object_id')

    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'enderecos'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        indexes = [
            models.Index(fields=['cep']),
            models.Index(fields=['cidade', 'estado']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id', 'principal']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'logradouro', 'numero', 'complemento',
                        'bairro', 'cidade', 'estado', 'cep', 'pais'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_endereco_completo_por_entidade_vivo',
            ),
            models.UniqueConstraint(
                fields=['content_type', 'object_id'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_endereco_principal_por_entidade_vivo',
            ),
        ]

    def delete(self, user=None):
        self.principal = False
        return super().delete(user=user)

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
