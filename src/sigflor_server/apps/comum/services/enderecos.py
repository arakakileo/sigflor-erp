from typing import Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from ..models import Endereco


class EnderecoService:
    """Service layer para operações com Endereço."""

    @staticmethod
    @transaction.atomic
    def create(
        entidade,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        principal: bool = False,
        created_by=None,
    ) -> Endereco:
        """Cria um novo Endereço para uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)

        # Se é principal, remove o principal anterior
        if principal:
            Endereco.objects.filter(
                content_type=content_type,
                object_id=str(entidade.pk),
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        endereco = Endereco(
            content_type=content_type,
            object_id=str(entidade.pk),
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            principal=principal,
            created_by=created_by,
        )
        endereco.save()
        return endereco

    @staticmethod
    @transaction.atomic
    def update(endereco: Endereco, updated_by=None, **kwargs) -> Endereco:
        """Atualiza um Endereço existente."""
        # Se está tornando principal, remove o principal anterior
        if kwargs.get('principal') and not endereco.principal:
            Endereco.objects.filter(
                content_type=endereco.content_type,
                object_id=endereco.object_id,
                principal=True,
                deleted_at__isnull=True
            ).exclude(pk=endereco.pk).update(principal=False)

        for attr, value in kwargs.items():
            if hasattr(endereco, attr):
                setattr(endereco, attr, value)
        endereco.updated_by = updated_by
        endereco.save()
        return endereco

    @staticmethod
    @transaction.atomic
    def delete(endereco: Endereco, user=None) -> None:
        """Soft delete de um Endereço."""
        endereco.delete(user=user)

    @staticmethod
    def get_enderecos_por_entidade(entidade) -> list:
        """Retorna todos os endereços de uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Endereco.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__isnull=True
        ).order_by('-principal', '-created_at'))

    @staticmethod
    def get_endereco_principal(entidade) -> Optional[Endereco]:
        """Retorna o endereço principal de uma entidade."""
        content_type = ContentType.objects.get_for_model(entidade)
        return Endereco.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            principal=True,
            deleted_at__isnull=True
        ).first()
