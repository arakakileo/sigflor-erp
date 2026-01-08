from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PessoaFisica
from .enderecos import EnderecoService
from .contatos import ContatoService
from .documentos import DocumentoService
from .anexos import AnexoService
from .deficiencias import DeficienciaService
from .utils import ServiceUtils


class PessoaFisicaService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        nome_completo: str,
        cpf: str,
        nome_mae: Optional[str] = None,
        nome_pai: Optional[str] = None,
        rg: Optional[str] = None,
        orgao_emissor: Optional[str] = None,
        data_nascimento=None,
        sexo: Optional[str] = None,
        estado_civil: Optional[str] = None,
        nacionalidade: Optional[str] = None,
        naturalidade: Optional[str] = None,
        observacoes: Optional[str] = None,
        created_by=None,
        enderecos: List[dict] = None,
        contatos: List[dict] = None,
        documentos: List[dict] = None,
        anexos: List[dict] = None,
        deficiencias: List[dict] = None,
    ) -> PessoaFisica:

        pessoa = PessoaFisica(
            nome_completo=nome_completo,
            nome_mae=nome_mae,
            nome_pai=nome_pai,
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

        if enderecos:
            for end_data in enderecos:
                EnderecoService.vincular_endereco_pessoa_fisica(
                    pessoa_fisica=pessoa, created_by=created_by, **end_data
                )

        if contatos:
            for ctt_data in contatos:
                ContatoService.vincular_contato_pessoa_fisica(
                    pessoa_fisica=pessoa, created_by=created_by, **ctt_data
                )

        if documentos:
            for doc_data in documentos:
                DocumentoService.vincular_documento_pessoa_fisica(
                    pessoa_fisica=pessoa, created_by=created_by, **doc_data
                )

        if anexos:
            for anx_data in anexos:
                AnexoService.create(
                    entidade=pessoa, created_by=created_by, **anx_data
                )

        if deficiencias:
            for def_data in deficiencias:
                DeficienciaService.create(
                    pessoa_fisica=pessoa, created_by=created_by, **def_data
                )

        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaFisica, updated_by=None, **kwargs) -> PessoaFisica:

        enderecos = kwargs.pop('enderecos', None)
        contatos = kwargs.pop('contatos', None)
        documentos = kwargs.pop('documentos', None)
        anexos = kwargs.pop('anexos', None)
        deficiencias = kwargs.pop('deficiencias', None)

        for attr, value in kwargs.items():
            if hasattr(pessoa, attr):
                setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()

        if enderecos is not None:
            EnderecoService.atualizar_enderecos_pessoa_fisica(
                pessoa, enderecos, updated_by
            )

        # if contatos is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=contatos,
        #         service_filho=ContatoService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_contatos_pessoa_fisica',
        #         metodo_criar='vincular_contato_pessoa_fisica',
        #         campo_entidade_pai='pessoa_fisica'
        #     )

        # if documentos is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=documentos,
        #         service_filho=DocumentoService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_documentos_pessoa_fisica',
        #         metodo_criar='vincular_documento_pessoa_fisica',
        #         campo_entidade_pai='pessoa_fisica'
        #     )

        # if anexos is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=anexos,
        #         service_filho=AnexoService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_anexos_por_entidade',
        #         # Defaults: metodo_criar='create', campo_entidade_pai='entidade'
        #     )

        # if deficiencias is not None:
        #     ServiceUtils.sincronizar_lista_aninhada(
        #         entidade_pai=pessoa,
        #         dados_lista=deficiencias,
        #         service_filho=DeficienciaService,
        #         user=updated_by,
        #         metodo_busca_existentes='get_deficiencias_pessoa_fisica',
        #         metodo_criar='create',
        #         campo_entidade_pai='pessoa_fisica'
        #     )

        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaFisica, user=None) -> None:
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaFisica, user=None) -> PessoaFisica:
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cpf(cpf: str) -> Optional[PessoaFisica]:
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
            novo_nome = defaults.get('nome_completo', '').strip()
            nome_banco = pessoa.nome_completo.strip()
            if novo_nome != nome_banco:
                raise ValidationError({
                    'cpf': (
                        f"O CPF {cpf} já consta no sistema vinculado a uma pessoa com nome diferente. "
                        f"Você informou '{novo_nome}', mas o registro original possui outro nome. "
                        "Verifique se o número do CPF está correto."
                    )
                })
            if defaults:
                user = defaults.get('created_by')
                PessoaFisicaService.update(pessoa, updated_by=user, **defaults)
            return pessoa, False
        return PessoaFisicaService.create(cpf=cpf_limpo, **defaults), True