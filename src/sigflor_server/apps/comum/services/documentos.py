from typing import Optional
import puremagic
from django.db import transaction
from django.db.models import QuerySet
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from datetime import timedelta

from ..models import (
    Documento, PessoaFisicaDocumento, PessoaJuridicaDocumento,
    PessoaFisica, PessoaJuridica
)
from ..validators.documentos import validar_tipo_arquivo


class DocumentoService:

    @staticmethod
    def _extrair_metadados_arquivo(arquivo: UploadedFile) -> dict:
        nome_original = arquivo.name
        tamanho = arquivo.size
        mimetype = None
        try:
            initial_pos = arquivo.tell() 
            arquivo.seek(0)
            header_bytes = arquivo.read(2048)
            mimetypes_found = puremagic.magic_string(header_bytes)

            if mimetypes_found:
                mimetype = mimetypes_found[0].mime_type
            arquivo.seek(initial_pos)

        except Exception:
            if arquivo.tell() != 0:
                arquivo.seek(0)
            mimetype = None

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
        
        metadados = DocumentoService._extrair_metadados_arquivo(arquivo)
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
    def update(documento: Documento, updated_by=None, **kwargs) -> Documento:
        campos_permitidos = ['tipo', 'descricao', 'data_emissao', 'data_validade']
        for attr, value in kwargs.items():
            if attr in campos_permitidos and hasattr(documento, attr):
                setattr(documento, attr, value)
        documento.updated_by = updated_by
        documento.save()
        return documento

    @staticmethod
    def _verificar_e_apagar_orfao(documento: Documento, user) -> None:

        if PessoaFisicaDocumento.objects.filter(documento=documento, deleted_at__isnull=True).exists():
            return
        
        if PessoaJuridicaDocumento.objects.filter(documento=documento, deleted_at__isnull=True).exists():
            return

        documento.delete(user=user)

    # =========================================================================
    # 1. PESSOA FÍSICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_documentos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        return PessoaFisicaDocumento.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('documento').order_by(
            'documento__tipo', '-created_at'
        )

    @staticmethod
    @transaction.atomic
    def vincular_documento_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        tipo: str,
        arquivo: UploadedFile,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        created_by=None,
    ) -> PessoaFisicaDocumento:
        
        documento = DocumentoService.create(
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            created_by=created_by,
        )

        vinculo = PessoaFisicaDocumento(
            pessoa_fisica=pessoa_fisica,
            documento=documento,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaDocumento, user=None) -> None:
        documento = vinculo.documento
        vinculo.delete(user=user)
        DocumentoService._verificar_e_apagar_orfao(documento, user)

    # =========================================================================
    # 2. PESSOA JURÍDICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_documentos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        return PessoaJuridicaDocumento.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('documento').order_by(
            'documento__tipo', '-created_at'
        )

    @staticmethod
    @transaction.atomic
    def vincular_documento_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        tipo: str,
        arquivo: UploadedFile,
        descricao: Optional[str] = None,
        data_emissao=None,
        data_validade=None,
        created_by=None,
    ) -> PessoaJuridicaDocumento:
        
        documento = DocumentoService.create(
            tipo=tipo,
            arquivo=arquivo,
            descricao=descricao,
            data_emissao=data_emissao,
            data_validade=data_validade,
            created_by=created_by,
        )

        vinculo = PessoaJuridicaDocumento(
            pessoa_juridica=pessoa_juridica,
            documento=documento,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaDocumento, user=None) -> None:
        documento = vinculo.documento
        vinculo.delete(user=user)
        DocumentoService._verificar_e_apagar_orfao(documento, user)

    # =========================================================================
    # 3. QUERIES DE NEGÓCIO (Alertas e Validade)
    # =========================================================================

    @staticmethod
    def get_documentos_a_vencer(dias: int = 30) -> QuerySet:
        data_limite = timezone.now().date() + timedelta(days=dias)
        return Documento.objects.filter(
            data_validade__lte=data_limite,
            data_validade__gte=timezone.now().date(),
            deleted_at__isnull=True
        ).order_by('data_validade')

    @staticmethod
    def get_documentos_vencidos() -> QuerySet:
        return Documento.objects.filter(
            data_validade__lt=timezone.now().date(),
            deleted_at__isnull=True
        ).order_by('data_validade')