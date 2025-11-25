from typing import Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import Contato


class ContatoService:
    """Service layer para operações com Contato."""

    @staticmethod
    @transaction.atomic
    def create(
        entidade,
        tipo: str,
        valor: str,
        principal: bool = False,
        created_by=None,
    ) -> Contato:
        """Cria um novo Contato para uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)

        # Se é principal, remove o principal anterior do mesmo tipo
        if principal:
            Contato.objects.filter(
                content_type=content_type,
                object_id=str(entidade.pk),
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        contato = Contato(
            content_type=content_type,
            object_id=str(entidade.pk),
            tipo=tipo,
            valor=valor,
            principal=principal,
            created_by=created_by,
        )
        contato.save()
        return contato

    @staticmethod
    @transaction.atomic
    def update(contato: Contato, updated_by=None, **kwargs) -> Contato:
        """Atualiza um Contato existente."""
        # Se está tornando principal, remove o principal anterior do mesmo tipo
        if kwargs.get('principal') and not contato.principal:
            Contato.objects.filter(
                content_type=contato.content_type,
                object_id=contato.object_id,
                tipo=contato.tipo,
                principal=True,
                deleted_at__isnull=True
            ).exclude(pk=contato.pk).update(principal=False)

        for attr, value in kwargs.items():
            if hasattr(contato, attr):
                setattr(contato, attr, value)
        contato.updated_by = updated_by
        contato.save()
        return contato

    @staticmethod
    @transaction.atomic
    def delete(contato: Contato, user=None) -> None:
        """Soft delete de um Contato."""
        contato.delete(user=user)

    @staticmethod
    def get_contatos_por_entidade(entidade) -> list:
        """Retorna todos os contatos de uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Contato.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__isnull=True
        ).order_by('tipo', '-principal', '-created_at'))

    @staticmethod
    def get_contato_principal_por_tipo(entidade, tipo: str) -> Optional[Contato]:
        """Retorna o contato principal de um tipo específico."""
        content_type = ContentType.objects.get_for_model(entidade)
        return Contato.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            tipo=tipo,
            principal=True,
            deleted_at__isnull=True
        ).first()
