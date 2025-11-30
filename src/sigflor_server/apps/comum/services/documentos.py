from typing import Optional, Union
import mimetypes
from django.db import transaction
from django.db.models import QuerySet
from django.core.files.uploadedfile import UploadedFile

from ..models import Documento, PessoaFisicaDocumento, PessoaJuridicaDocumento
from ..models import PessoaFisica, PessoaJuridica
from ..validators.documentos import validar_tipo_arquivo


class DocumentoService:
    """Service layer para operações com Documento."""

    @staticmethod
    def _extrair_metadados_arquivo(arquivo: UploadedFile) -> dict:
        """Extrai metadados do arquivo enviado."""
        nome_original = arquivo.name
        tamanho = arquivo.size

        # Tenta detectar o mimetype
        mimetype = arquivo.content_type
        if not mimetype or mimetype == 'application/octet-stream':
            # Fallback para detecção por extensão
            guessed_type, _ = mimetypes.guess_type(nome_original)
            mimetype = guessed_type or 'application/octet-stream'

        return {
            'nome_original': nome_original,
            'mimetype': mimetype,
            'tamanho': tamanho,
        }

    @staticmethod
    @transaction.atomic
    def create(
        *,
        tipo: str,
        arquivo: UploadedFile,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        created_by=None,
    ) -> Documento:
        """Cria um novo Documento (sem vínculo com entidade)."""
        metadados = DocumentoService._extrair_metadados_arquivo(arquivo)

        # Valida o tipo do arquivo
        validar_tipo_arquivo(metadados['mimetype'])

        documento = Documento(
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            created_by=created_by,
            **metadados
        )
        documento.save()
        return documento

    @staticmethod
    @transaction.atomic
    def add_documento_to_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        tipo: str,
        arquivo: UploadedFile,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        principal: bool = False,
        created_by=None,
    ) -> PessoaFisicaDocumento:
        """
        Cria um documento e vincula a uma PessoaFisica.
        Se principal=True, desmarca outros documentos do mesmo tipo como principal.
        """
        # Cria o documento
        documento = DocumentoService.create(
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            created_by=created_by,
        )

        # Se é principal, desmarca outros do mesmo tipo
        if principal:
            PessoaFisicaDocumento.objects.filter(
                pessoa_fisica=pessoa_fisica,
                documento__tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        # Cria o vínculo
        vinculo = PessoaFisicaDocumento(
            pessoa_fisica=pessoa_fisica,
            documento=documento,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def add_documento_to_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        tipo: str,
        arquivo: UploadedFile,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaDocumento:
        """
        Cria um documento e vincula a uma PessoaJuridica.
        Se principal=True, desmarca outros documentos do mesmo tipo como principal.
        """
        # Cria o documento
        documento = DocumentoService.create(
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            created_by=created_by,
        )

        # Se é principal, desmarca outros do mesmo tipo
        if principal:
            PessoaJuridicaDocumento.objects.filter(
                pessoa_juridica=pessoa_juridica,
                documento__tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        # Cria o vínculo
        vinculo = PessoaJuridicaDocumento(
            pessoa_juridica=pessoa_juridica,
            documento=documento,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def set_principal_pessoa_fisica(
        *,
        vinculo: PessoaFisicaDocumento,
        updated_by=None,
    ) -> PessoaFisicaDocumento:
        """Define um documento como principal para uma PessoaFisica."""
        # Desmarca outros do mesmo tipo
        PessoaFisicaDocumento.objects.filter(
            pessoa_fisica=vinculo.pessoa_fisica,
            documento__tipo=vinculo.documento.tipo,
            principal=True,
            deleted_at__isnull=True
        ).exclude(pk=vinculo.pk).update(principal=False)

        vinculo.principal = True
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def set_principal_pessoa_juridica(
        *,
        vinculo: PessoaJuridicaDocumento,
        updated_by=None,
    ) -> PessoaJuridicaDocumento:
        """Define um documento como principal para uma PessoaJuridica."""
        # Desmarca outros do mesmo tipo
        PessoaJuridicaDocumento.objects.filter(
            pessoa_juridica=vinculo.pessoa_juridica,
            documento__tipo=vinculo.documento.tipo,
            principal=True,
            deleted_at__isnull=True
        ).exclude(pk=vinculo.pk).update(principal=False)

        vinculo.principal = True
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def update(documento: Documento, updated_by=None, **kwargs) -> Documento:
        """Atualiza um Documento existente (metadados, não arquivo)."""
        allowed_fields = ['tipo', 'descricao', 'data_emissao', 'data_validade']
        for attr, value in kwargs.items():
            if attr in allowed_fields and hasattr(documento, attr):
                setattr(documento, attr, value)
        documento.updated_by = updated_by
        documento.save()
        return documento

    @staticmethod
    @transaction.atomic
    def delete(documento: Documento, user=None) -> None:
        """Soft delete de um Documento e seus vínculos."""
        # Remove vínculos
        PessoaFisicaDocumento.objects.filter(
            documento=documento,
            deleted_at__isnull=True
        ).update(deleted_at=documento.deleted_at)
        PessoaJuridicaDocumento.objects.filter(
            documento=documento,
            deleted_at__isnull=True
        ).update(deleted_at=documento.deleted_at)
        # Remove documento
        documento.delete(user=user)

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaDocumento, user=None) -> None:
        """Remove o vínculo de um documento com uma PessoaFisica."""
        vinculo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaDocumento, user=None) -> None:
        """Remove o vínculo de um documento com uma PessoaJuridica."""
        vinculo.delete(user=user)

    @staticmethod
    def get_documentos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        """Retorna todos os documentos de uma PessoaFisica."""
        return PessoaFisicaDocumento.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('documento').order_by(
            'documento__tipo', '-principal', '-created_at'
        )

    @staticmethod
    def get_documentos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        """Retorna todos os documentos de uma PessoaJuridica."""
        return PessoaJuridicaDocumento.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('documento').order_by(
            'documento__tipo', '-principal', '-created_at'
        )

    @staticmethod
    def get_documentos_a_vencer(dias: int = 30) -> QuerySet:
        """Retorna documentos cuja data_validade está dentro do prazo especificado."""
        from django.utils import timezone
        from datetime import timedelta

        data_limite = timezone.now().date() + timedelta(days=dias)
        return Documento.objects.filter(
            data_validade__lte=data_limite,
            data_validade__gte=timezone.now().date(),
            deleted_at__isnull=True
        ).order_by('data_validade')

    @staticmethod
    def get_documentos_vencidos() -> QuerySet:
        """Retorna todos os documentos vencidos."""
        from django.utils import timezone

        return Documento.objects.filter(
            data_validade__lt=timezone.now().date(),
            deleted_at__isnull=True
        ).order_by('data_validade')
