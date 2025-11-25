from typing import Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import Anexo


class AnexoService:
    """Service layer para operações com Anexo."""

    @staticmethod
    @transaction.atomic
    def create(
        entidade,
        arquivo,
        nome_original: Optional[str] = None,
        descricao: Optional[str] = None,
        mimetype: Optional[str] = None,
        created_by=None,
    ) -> Anexo:
        """Cria um novo Anexo para uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)

        # Extrai metadados do arquivo
        if not nome_original and hasattr(arquivo, 'name'):
            nome_original = arquivo.name

        tamanho = arquivo.size if hasattr(arquivo, 'size') else 0

        if not mimetype and hasattr(arquivo, 'content_type'):
            mimetype = arquivo.content_type

        anexo = Anexo(
            content_type=content_type,
            object_id=str(entidade.pk),
            arquivo=arquivo,
            nome_original=nome_original,
            descricao=descricao,
            tamanho=tamanho,
            mimetype=mimetype or 'application/octet-stream',
            created_by=created_by,
        )
        anexo.save()
        return anexo

    @staticmethod
    @transaction.atomic
    def update(anexo: Anexo, updated_by=None, **kwargs) -> Anexo:
        """Atualiza um Anexo existente (apenas metadados)."""
        # Não permite alterar arquivo
        kwargs.pop('arquivo', None)
        kwargs.pop('tamanho', None)
        kwargs.pop('mimetype', None)

        for attr, value in kwargs.items():
            if hasattr(anexo, attr):
                setattr(anexo, attr, value)
        anexo.updated_by = updated_by
        anexo.save()
        return anexo

    @staticmethod
    @transaction.atomic
    def delete(anexo: Anexo, user=None) -> None:
        """Soft delete de um Anexo."""
        anexo.delete(user=user)

    @staticmethod
    def get_anexos_por_entidade(entidade) -> list:
        """Retorna todos os anexos de uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Anexo.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__isnull=True
        ).order_by('-created_at'))

    @staticmethod
    def get_anexos_por_mimetype(entidade, mimetype: str) -> list:
        """Retorna anexos de um tipo MIME específico."""
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Anexo.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            mimetype__startswith=mimetype,
            deleted_at__isnull=True
        ))
