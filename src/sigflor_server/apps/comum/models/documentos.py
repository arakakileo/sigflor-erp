import uuid
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel
from .enums import TipoDocumento


def documento_upload_path(instance, filename):
    from django.utils import timezone
    now = timezone.now()
    return f'documentos/{now.year}/{now.month:02d}/{filename}'


class Documento(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=50, choices=TipoDocumento.choices)
    descricao = models.TextField(blank=True, default='')
    arquivo = models.FileField(upload_to=documento_upload_path)

    nome_original = models.CharField(
        max_length=255,
        help_text='Nome do arquivo no momento do upload'
    )
    mimetype = models.CharField(
        max_length=100,
        help_text='Tipo MIME do arquivo (ex: application/pdf)'
    )
    tamanho = models.PositiveIntegerField(
        help_text='Tamanho do arquivo em bytes'
    )

    data_emissao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['data_validade']),
            models.Index(fields=['tipo', 'data_emissao']),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome_original}"

    @property
    def vencido(self) -> bool:
        """Verifica se o documento está vencido."""
        from django.utils import timezone
        if self.data_validade:
            return self.data_validade < timezone.now().date()
        return False


class PessoaFisicaDocumento(SoftDeleteModel):

    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='documentos_vinculados'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_fisica'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o documento principal deste tipo para esta pessoa'
    )

    class Meta:
        db_table = 'pessoas_fisicas_documentos'
        verbose_name = 'Documento de Pessoa Física'
        verbose_name_plural = 'Documentos de Pessoas Físicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_fisica', 'documento'],
                name='uniq_pf_documento'
            ),
            # Apenas um documento principal por tipo por pessoa física
            models.UniqueConstraint(
                fields=['pessoa_fisica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pf_documento_principal_por_tipo',
                # Nota: a constraint de unicidade por tipo será verificada no service
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_fisica} - {self.documento}"


class PessoaJuridicaDocumento(SoftDeleteModel):

    pessoa_juridica = models.ForeignKey(
        'comum.PessoaJuridica',
        on_delete=models.CASCADE,
        related_name='documentos_vinculados'
    )
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='vinculos_pessoa_juridica'
    )
    principal = models.BooleanField(
        default=False,
        help_text='Indica se é o documento principal deste tipo para esta pessoa jurídica'
    )

    class Meta:
        db_table = 'pessoas_juridicas_documentos'
        verbose_name = 'Documento de Pessoa Jurídica'
        verbose_name_plural = 'Documentos de Pessoas Jurídicas'
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_juridica', 'documento'],
                name='uniq_pj_documento'
            ),
            models.UniqueConstraint(
                fields=['pessoa_juridica'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_pj_documento_principal_por_tipo',
            ),
        ]

    def __str__(self):
        return f"{self.pessoa_juridica} - {self.documento}"
