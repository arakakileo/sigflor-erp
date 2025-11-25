import uuid
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .base import SoftDeleteModel


def documento_upload_path(instance, filename):
    """Define o caminho de upload para documentos."""
    return f'documentos/{instance.content_type.model}/{instance.object_id}/{filename}'


class Documento(SoftDeleteModel):
    """
    Entidade genérica de documentos utilizando GenericForeignKey.
    Para arquivos formais, certificados e juridicamente relevantes.
    """

    class TipoDocumento(models.TextChoices):
        IDENTIDADE = 'identidade', 'Identidade (RG)'
        CPF = 'cpf', 'CPF'
        CNH = 'cnh', 'CNH'
        CONTRATO_SOCIAL = 'contrato_social', 'Contrato Social'
        COMPROVANTE_ENDERECO = 'comprovante_endereco', 'Comprovante de Endereço'
        NOTA_FISCAL = 'nota_fiscal', 'Nota Fiscal'
        ASO = 'aso', 'ASO (Atestado de Saúde Ocupacional)'
        LAUDO = 'laudo', 'Laudo'
        MANUAL = 'manual', 'Manual'
        CONTRATO = 'contrato', 'Contrato'
        ADITIVO = 'aditivo', 'Aditivo'
        CRLV = 'crlv', 'CRLV'
        CERTIDAO = 'certidao', 'Certidão'
        OUTRO = 'outro', 'Outro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=50, choices=TipoDocumento.choices)
    descricao = models.TextField(blank=True, null=True)
    arquivo = models.FileField(upload_to=documento_upload_path)

    # GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID como string
    entidade = GenericForeignKey('content_type', 'object_id')

    data_emissao = models.DateField(blank=True, null=True)
    data_validade = models.DateField(blank=True, null=True)
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = 'documentos'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type', 'object_id', 'tipo']),
            models.Index(fields=['data_validade']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['content_type', 'object_id', 'tipo'],
                condition=Q(principal=True, deleted_at__isnull=True),
                name='uniq_documento_principal_por_tipo_entidade',
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.entidade}"

    @property
    def vencido(self) -> bool:
        """Verifica se o documento está vencido."""
        from django.utils import timezone
        if self.data_validade:
            return self.data_validade < timezone.now().date()
        return False

    @property
    def nome_arquivo(self) -> str:
        """Retorna apenas o nome do arquivo."""
        if self.arquivo:
            return self.arquivo.name.split('/')[-1]
        return ''
