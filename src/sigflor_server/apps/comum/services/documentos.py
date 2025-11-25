from typing import Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import Documento


class DocumentoService:
    """Service layer para operações com Documento."""

    @staticmethod
    @transaction.atomic
    def create(
        entidade,
        tipo: str,
        arquivo,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        principal: bool = False,
        created_by=None,
    ) -> Documento:
        """Cria um novo Documento para uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)

        # Se é principal, remove o principal anterior do mesmo tipo
        if principal:
            Documento.objects.filter(
                content_type=content_type,
                object_id=str(entidade.pk),
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        documento = Documento(
            content_type=content_type,
            object_id=str(entidade.pk),
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            principal=principal,
            created_by=created_by,
        )
        documento.save()
        return documento

    @staticmethod
    @transaction.atomic
    def update(documento: Documento, updated_by=None, **kwargs) -> Documento:
        """Atualiza um Documento existente."""
        # Se está tornando principal, remove o principal anterior do mesmo tipo
        if kwargs.get('principal') and not documento.principal:
            Documento.objects.filter(
                content_type=documento.content_type,
                object_id=documento.object_id,
                tipo=documento.tipo,
                principal=True,
                deleted_at__isnull=True
            ).exclude(pk=documento.pk).update(principal=False)

        for attr, value in kwargs.items():
            if hasattr(documento, attr):
                setattr(documento, attr, value)
        documento.updated_by = updated_by
        documento.save()
        return documento

    @staticmethod
    @transaction.atomic
    def delete(documento: Documento, user=None) -> None:
        """Soft delete de um Documento."""
        documento.delete(user=user)

    @staticmethod
    def get_documentos_por_entidade(entidade) -> list:
        """Retorna todos os documentos de uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Documento.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__isnull=True
        ).order_by('tipo', '-principal', '-created_at'))

    @staticmethod
    def get_documentos_vencidos(entidade) -> list:
        """Retorna documentos vencidos de uma entidade."""
        from django.utils import timezone
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Documento.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            data_validade__lt=timezone.now().date(),
            deleted_at__isnull=True
        ))
