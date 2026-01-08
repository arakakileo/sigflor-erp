from typing import Optional, List , Dict, Any
from django.db import transaction

from ..models import PessoaJuridica, SituacaoCadastral

from .enderecos import EnderecoService
from .contatos import ContatoService
from .documentos import DocumentoService
from .anexos import AnexoService
from apps.autenticacao.models import Usuario
from .utils import ServiceUtils


class PessoaJuridicaService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        razao_social: str,
        cnpj: str,
        nome_fantasia: Optional[str] = None,
        inscricao_estadual: Optional[str] = None,
        data_abertura=None,
        situacao_cadastral: str = SituacaoCadastral.ATIVA,
        observacoes: Optional[str] = None,
        created_by:Usuario=None,
        enderecos: List[Dict[str, Any]] = None,
        contatos: List[Dict[str, Any]] = None,
        documentos: List[Dict[str, Any]] = None,
        anexos: List[Dict[str, Any]] = None,
    ) -> PessoaJuridica:
        
        pessoa = PessoaJuridica(
            razao_social=razao_social,
            cnpj=cnpj,
            nome_fantasia=nome_fantasia,
            inscricao_estadual=inscricao_estadual,
            data_abertura=data_abertura,
            situacao_cadastral=situacao_cadastral,
            observacoes=observacoes,
            created_by=created_by,
        )
        pessoa.save()

        if enderecos:
            for end_data in enderecos:
                EnderecoService.vincular_endereco_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **end_data
                )

        if contatos:
            for ctt_data in contatos:
                ContatoService.vincular_contato_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **ctt_data
                )

        if documentos:
            for doc_data in documentos:
                doc_data.pop('id', None)
                DocumentoService.vincular_documento_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **doc_data
                )

        if anexos:
            for anx_data in anexos:
                anx_data.pop('id', None)
                AnexoService.create(
                    entidade=pessoa,
                    created_by=created_by,
                    **anx_data
                )

        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaJuridica, updated_by=None, **kwargs) -> PessoaJuridica:

        enderecos = kwargs.pop('enderecos', None)
        contatos = kwargs.pop('contatos', None)
        documentos = kwargs.pop('documentos', None)
        anexos = kwargs.pop('anexos', None)
        for attr, value in kwargs.items():
            if hasattr(pessoa, attr): setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()

        if enderecos is not None:
            EnderecoService.atualizar_enderecos_pessoa_juridica(
                pessoa, enderecos, updated_by
            )

        if contatos is not None:
            ContatoService.atualizar_contatos_pessoa_juridica(
                pessoa, contatos, updated_by
            )


        # if documentos is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=documentos,
        #         service_filho=DocumentoService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_documentos_pessoa_juridica',
        #         metodo_criar='vincular_documento_pessoa_juridica',
        #         campo_entidade_pai='pessoa_juridica'
        #     )

        # if anexos is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=anexos,
        #         service_filho=AnexoService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_anexos_por_entidade',
        #         # Defaults: metodo_criar='create', campo_entidade_pai='entidade' (Funciona para Anexo GFK)
        #     )

        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaJuridica, user=None) -> None:
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaJuridica, user=None) -> PessoaJuridica:
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cnpj(cnpj: str) -> Optional[PessoaJuridica]:
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        return PessoaJuridica.objects.filter(
            cnpj=cnpj_limpo,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_or_create_by_cnpj(
        *,
        cnpj: str,
        created_by:Usuario=None,
        **defaults
    ) -> tuple[PessoaJuridica, bool]:

        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        pessoa = PessoaJuridicaService.get_by_cnpj(cnpj_limpo)
        if pessoa:
            return pessoa, False
            # raise ValidationError({
            #     'cnpj': "Esta Pessoa Jurídica já está cadastrada no sistema."
            # })

        defaults['cnpj'] = cnpj_limpo
        defaults['created_by'] = created_by
        return PessoaJuridicaService.create(**defaults), True
