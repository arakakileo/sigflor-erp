import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .base import SoftDeleteModel


def anexo_upload_path(instance, filename):
    """Define o caminho de upload para anexos."""
    return f'anexos/{instance.content_type.model}/{instance.object_id}/{filename}'


class Anexo(SoftDeleteModel):
    """
    Entidade genérica de anexos utilizando GenericForeignKey.
    Para arquivos complementares e de natureza menos formal que Documentos.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome_original = models.CharField(max_length=255, help_text="Nome original do arquivo enviado")
    arquivo = models.FileField(upload_to=anexo_upload_path)
    descricao = models.TextField(blank=True, null=True)

    # GenericForeignKey
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)  # UUID como string
    entidade = GenericForeignKey('content_type', 'object_id')

    tamanho = models.BigIntegerField(help_text="Tamanho do arquivo em bytes")
    mimetype = models.CharField(max_length=100, help_text="Tipo MIME do arquivo")

    class Meta:
        db_table = 'anexos'
        verbose_name = 'Anexo'
        verbose_name_plural = 'Anexos'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['mimetype']),
        ]

    def save(self, *args, **kwargs):
        # Extrai metadados do arquivo se não fornecidos
        if self.arquivo and not self.nome_original:
            self.nome_original = self.arquivo.name.split('/')[-1]
        if self.arquivo and not self.tamanho:
            self.tamanho = self.arquivo.size
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_original} ({self.tamanho_formatado})"

    @property
    def tamanho_formatado(self) -> str:
        """Retorna o tamanho do arquivo formatado."""
        if self.tamanho < 1024:
            return f"{self.tamanho} B"
        elif self.tamanho < 1024 * 1024:
            return f"{self.tamanho / 1024:.1f} KB"
        elif self.tamanho < 1024 * 1024 * 1024:
            return f"{self.tamanho / (1024 * 1024):.1f} MB"
        else:
            return f"{self.tamanho / (1024 * 1024 * 1024):.1f} GB"

    @property
    def extensao(self) -> str:
        """Retorna a extensão do arquivo."""
        if '.' in self.nome_original:
            return self.nome_original.rsplit('.', 1)[-1].lower()
        return ''
