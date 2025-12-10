from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PessoaFisica, Endereco, Contato, Documento, Anexo
from .enderecos import EnderecoService
from .contatos import ContatoService
from .documentos import DocumentoService
from .anexos import AnexoService
from .utils import ServiceUtils


class PessoaFisicaService:
    """Service layer para operações com Pessoa Física."""

    @staticmethod
    @transaction.atomic
    def create(
        nome_completo: str,
        cpf: str,
        rg: Optional[str] = None,
        orgao_emissor: Optional[str] = None,
        data_nascimento=None,
        sexo: Optional[str] = None,
        estado_civil: Optional[str] = None,
        nacionalidade: Optional[str] = None,
        naturalidade: Optional[str] = None,
        observacoes: Optional[str] = None,
        created_by=None,
        enderecos_vinculados: List[dict] = [],
        contatos_vinculados: List[dict] = [],
        documentos_vinculados: List[dict] = [],
        anexos_vinculados: List[dict] = [],
    ) -> PessoaFisica:
        """Cria uma nova Pessoa Física e suas entidades relacionadas."""
        pessoa = PessoaFisica(
            nome_completo=nome_completo,
            cpf=cpf,
            rg=rg,
            orgao_emissor=orgao_emissor,
            data_nascimento=data_nascimento,
            sexo=sexo,
            estado_civil=estado_civil,
            nacionalidade=nacionalidade,
            naturalidade=naturalidade,
            observacoes=observacoes,
            created_by=created_by,
        )
        pessoa.save()

        if enderecos_vinculados:
            for end_data in enderecos_vinculados:
                EnderecoService.criar_endereco_pessoa_fisica(pessoa_fisica=pessoa, created_by=created_by, **end_data)
        
        if contatos_vinculados:
            for ctt_data in contatos_vinculados:
                ContatoService.add_contato_to_pessoa_fisica(pessoa_fisica=pessoa, created_by=created_by, **ctt_data)

        if documentos_vinculados:
            for doc_data in documentos_vinculados:
                DocumentoService.add_documento_to_pessoa_fisica(pessoa_fisica=pessoa, created_by=created_by, **doc_data)

        if anexos_vinculados:
            for anx_data in anexos_vinculados:
                AnexoService.create(entidade=pessoa, created_by=created_by, **anx_data)

        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaFisica, updated_by=None, **kwargs) -> PessoaFisica:
        """Atualiza uma Pessoa Física e sincroniza suas listas aninhadas."""
        
        enderecos = kwargs.pop('enderecos', None)
        contatos = kwargs.pop('contatos', None)
        documentos = kwargs.pop('documentos', None)
        anexos = kwargs.pop('anexos', None)

        for attr, value in kwargs.items():
            if hasattr(pessoa, attr):
                setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()

        if enderecos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=pessoa,
                dados_lista=enderecos,
                service_filho=EnderecoService,
                model_filho=Endereco,
                user=updated_by,
                metodo_busca_existentes='get_enderecos_por_entidade'
            )

        if contatos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=pessoa,
                dados_lista=contatos,
                service_filho=ContatoService,
                model_filho=Contato,
                user=updated_by,
                metodo_busca_existentes='get_contatos_por_entidade'
            )

        if documentos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=pessoa,
                dados_lista=documentos,
                service_filho=DocumentoService,
                model_filho=Documento,
                user=updated_by,
                metodo_busca_existentes='get_documentos_por_entidade'
            )

        if anexos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=pessoa,
                dados_lista=anexos,
                service_filho=AnexoService,
                model_filho=Anexo,
                user=updated_by,
                metodo_busca_existentes='get_anexos_por_entidade'
            )

        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaFisica, user=None) -> None:
        """Soft delete de uma Pessoa Física."""
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaFisica, user=None) -> PessoaFisica:
        """Restaura uma Pessoa Física excluída."""
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cpf(cpf: str) -> Optional[PessoaFisica]:
        """Busca Pessoa Física por CPF."""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        return PessoaFisica.objects.filter(
            cpf=cpf_limpo,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_or_create_by_cpf(cpf: str, **defaults) -> tuple[PessoaFisica, bool]:
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        pessoa = PessoaFisicaService.get_by_cpf(cpf_limpo)
        if pessoa:
            return pessoa, False
            # raise ValidationError({'cpf': "Esta Pessoa Física já está cadastrada no sistema."})
        return PessoaFisicaService.create(cpf=cpf_limpo, **defaults), True
