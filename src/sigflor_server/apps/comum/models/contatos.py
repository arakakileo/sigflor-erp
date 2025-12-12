import uuid
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel
from ..validators import ContatosValidator
from .enums import TipoContato


class Contato(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoContato.choices)
    valor = models.CharField(max_length=150)
    tem_whatsapp = models.BooleanField(default=False)

    class Meta:
        db_table = 'contatos'
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['valor']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tipo', 'valor'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_contato_tipo_valor_vivo'
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.tipo == TipoContato.EMAIL:
            self.valor = ContatosValidator.normalizar_email(self.valor)
        elif self.tipo == TipoContato.FIXO:
            self.valor = ContatosValidator.normalizar_telefone_fixo(self.valor)
        elif self.tipo == TipoContato.CELULAR:
            self.valor = ContatosValidator.normalizar_telefone_celular(self.valor)
        else:
            self.valor = (self.valor or '').strip()

    def __str__(self) -> str:
        valor_exibicao = (
            self.valor_formatado
            if self.tipo in (TipoContato.CELULAR, TipoContato.FIXO)
            else self.valor
        )
        return f"{self.get_tipo_display()}: {valor_exibicao}"

    @property
    def valor_formatado(self) -> str:
        if self.tipo == TipoContato.CELULAR and self.valor.isdigit():
            if len(self.valor) == 11:
                return f"({self.valor[:2]}) {self.valor[2:7]}-{self.valor[7:]}"
        if self.tipo == TipoContato.FIXO and self.valor.isdigit():
            if len(self.valor) == 10:
                return f"({self.valor[:2]}) {self.valor[2:6]}-{self.valor[6:]}"
        return self.valor


class PessoaFisicaContato(SoftDeleteModel):
    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='contatos_vinculados'
    )
    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_fisica'
    )
    principal = models.BooleanField(default=False)
    contato_emergencia = models.BooleanField(
        default=False,
        help_text='Indica se é um contato de emergência'
    )

    class Meta:
        db_table = 'pessoas_fisicas_contatos'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_fisica', 'contato'],
                name='uniq_pf_contato'
            ),
            models.UniqueConstraint(
                fields=['pessoa_fisica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pf_contato_principal'
            ),
        ]


class PessoaJuridicaContato(SoftDeleteModel):
    """Tabela de ligação entre PessoaJuridica e Contato."""
    pessoa_juridica = models.ForeignKey(
        'comum.PessoaJuridica',
        on_delete=models.CASCADE,
        related_name='contatos_vinculados'
    )
    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_juridica'
    )
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'pessoas_juridicas_contatos'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica', 'contato'],
                name='uniq_pj_contato'
            ),
            models.UniqueConstraint(
                fields=['pessoa_juridica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pj_contato_principal'
            ),
        ]


class FilialContato(SoftDeleteModel):
    filial = models.ForeignKey(
        'comum.Filial',
        on_delete=models.CASCADE,
        related_name='contatos_vinculados'
    )
    contato = models.ForeignKey(
        Contato,
        on_delete=models.CASCADE,
        related_name='vinculos_filial'
    )
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'filiais_contatos'
        constraints = [
            models.UniqueConstraint(
                fields=['filial', 'contato'],
                name='uniq_filial_contato'
            ),
            models.UniqueConstraint(
                fields=['filial'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_filial_contato_principal'
            ),
        ]
