from typing import Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta

from ..models import Anexo


class AnexoService:

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
        content_type = ContentType.objects.get_for_model(entidade)

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
        anexo.delete(user=user)

    @staticmethod
    def get_anexos_por_entidade(entidade) -> list:
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Anexo.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__isnull=True
        ).order_by('-created_at'))

    @staticmethod
    def get_anexos_por_mimetype(entidade, mimetype: str) -> list:
        content_type = ContentType.objects.get_for_model(entidade)
        return list(Anexo.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            mimetype__startswith=mimetype,
            deleted_at__isnull=True
        ))

    @staticmethod
    def restaurar_anexos_entidade(entidade, data_delecao_pai, user):
        """
        Restaura anexos vinculados a qualquer entidade via GFK.
        """
        if not data_delecao_pai: return
        
        margem = timedelta(seconds=5)
        inicio = data_delecao_pai - margem
        fim = data_delecao_pai + margem

        content_type = ContentType.objects.get_for_model(entidade)
        
        anexos = Anexo.objects.filter(
            content_type=content_type,
            object_id=str(entidade.pk),
            deleted_at__range=(inicio, fim)
        )
        
        for anexo in anexos:
            anexo.restore(user=user)