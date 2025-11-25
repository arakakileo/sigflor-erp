import uuid
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .base import SoftDeleteModel
from ..validators import ContatosValidator


class Contato(SoftDeleteModel):
    """
    Entidade genérica de contatos utilizando GenericForeignKey.
    Pode ser vinculada a qualquer entidade do sistema.
    """

    class Tipo(models.TextChoices):
        CELULAR = 'telefone_celular', 'Telefone Celular'
        FIXO = 'telefone_fixo', 'Telefone Fixo'
        EMAIL = 'email', 'E-mail'
        OUTRO = 'outro', 'Outro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    valor = models.CharField(max_length=150)
    principal = models.BooleanField(default=False)

    # GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID como string
    entidade = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'contatos'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['valor']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id', 'tipo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'tipo', 'valor'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_contatos_tipo_valor_entidade'
            ),
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'tipo'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_contato_principal_por_tipo_entidade',
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.tipo == self.Tipo.EMAIL:
            self.valor = ContatosValidator.normalizar_email(self.valor)
        elif self.tipo == self.Tipo.FIXO:
            self.valor = ContatosValidator.normalizar_telefone_fixo(self.valor)
        elif self.tipo == self.Tipo.CELULAR:
            self.valor = ContatosValidator.normalizar_telefone_celular(self.valor)
        else:
            self.valor = (self.valor or '').strip()

    def __str__(self) -> str:
        valor_exibicao = (
            self.valor_formatado
            if self.tipo in (self.Tipo.CELULAR, self.Tipo.FIXO)
            else self.valor
        )
        return f"{self.get_tipo_display()}: {valor_exibicao}"

    @property
    def valor_formatado(self) -> str:
        if self.tipo == self.Tipo.CELULAR and self.valor.isdigit():
            if len(self.valor) == 11:
                return f"({self.valor[:2]}) {self.valor[2:7]}-{self.valor[7:]}"
        if self.tipo == self.Tipo.FIXO and self.valor.isdigit():
            if len(self.valor) == 10:
                return f"({self.valor[:2]}) {self.valor[2:6]}-{self.valor[6:]}"
        return self.valor
