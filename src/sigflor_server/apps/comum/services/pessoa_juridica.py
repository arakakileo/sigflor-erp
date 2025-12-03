from typing import Optional, List , Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PessoaJuridica, SituacaoCadastral
from .enderecos import EnderecoService
from .contatos import ContatoService
from .documentos import DocumentoService
from .anexos import AnexoService


class PessoaJuridicaService:
    """Service layer para operações com Pessoa Jurídica."""

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
        created_by=None,
        enderecos: List[Dict[str, Any]] = None,
        contatos: List[Dict[str, Any]] = None,
        documentos: List[Dict[str, Any]] = None,
        anexos: List[Dict[str, Any]] = None,
    ) -> PessoaJuridica:
        """Cria uma nova Pessoa Jurídica e suas entidades relacionadas."""
        
        # 1. Cria a entidade principal
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

        # 2. Processa Endereços
        if enderecos:
            for end_data in enderecos:
                EnderecoService.criar_endereco_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **end_data
                )

        # 3. Processa Contatos
        if contatos:
            for ctt_data in contatos:
                ContatoService.criar_contato_para_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **ctt_data
                )

        # 4. Processa Documentos
        if documentos:
            for doc_data in documentos:
                doc_data.pop('id', None)
                DocumentoService.add_documento_to_pessoa_juridica(
                    pessoa_juridica=pessoa,
                    created_by=created_by,
                    **doc_data
                )

        # 5. Processa Anexos (GFK)
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
        """
        Atualiza uma Pessoa Jurídica e sincroniza suas listas aninhadas.
        """
        enderecos_data = kwargs.pop('enderecos', None)
        contatos_data = kwargs.pop('contatos', None)
        documentos_data = kwargs.pop('documentos', None)
        anexos_data = kwargs.pop('anexos', None)

        # 1. Atualiza dados da entidade principal
        allowed_fields = [
            'razao_social', 'nome_fantasia', 'inscricao_estadual',
            'data_abertura', 'situacao_cadastral', 'observacoes'
        ]
        for attr, value in kwargs.items():
            if attr in allowed_fields and hasattr(pessoa, attr):
                setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()

        # 2. Sincroniza Endereços
        if enderecos_data is not None:
            # Mapeia vínculos existentes por ID
            vinculos_db = {str(v.id): v for v in pessoa.enderecos_vinculados.all()}
            ids_recebidos = set()

            for item in enderecos_data:
                item_id = item.get('id')
                
                if item_id and str(item_id) in vinculos_db:
                    # ATUALIZAR
                    ids_recebidos.add(str(item_id))
                    vinculo = vinculos_db[str(item_id)]
                    
                    # Atualiza campos do vínculo
                    if 'tipo' in item: vinculo.tipo = item['tipo']
                    if 'principal' in item:
                        if item['principal'] and not vinculo.principal:
                            # Se virou principal, usa o serviço para desmarcar outros
                            EnderecoService.set_principal_pessoa_juridica(vinculo=vinculo, updated_by=updated_by)
                        else:
                            vinculo.principal = item['principal']
                            vinculo.save()
                    
                    # Atualiza campos do endereço
                    EnderecoService.update(vinculo.endereco, updated_by=updated_by, **item)
                
                else:
                    # CRIAR NOVO
                    item.pop('id', None)
                    EnderecoService.criar_endereco_pessoa_juridica(
                        pessoa_juridica=pessoa,
                        created_by=updated_by,
                        **item
                    )

            # EXCLUIR REMOVIDOS
            for vid, vinculo in vinculos_db.items():
                if vid not in ids_recebidos:
                    EnderecoService.remove_vinculo_pessoa_juridica(vinculo, user=updated_by)

        # 3. Sincroniza Contatos
        if contatos_data is not None:
            vinculos_db = {str(v.id): v for v in pessoa.contatos_vinculados.all()}
            ids_recebidos = set()

            for item in contatos_data:
                item_id = item.get('id')

                if item_id and str(item_id) in vinculos_db:
                    ids_recebidos.add(str(item_id))
                    vinculo = vinculos_db[str(item_id)]

                    if 'principal' in item:
                        if item['principal'] and not vinculo.principal:
                            # ContatoService não tem método set_principal específico exposto no último snippet,
                            # mas podemos fazer manual ou implementar lá. Vamos fazer manual seguro aqui.
                            if item['principal']:
                                pessoa.contatos_vinculados.filter(principal=True).update(principal=False)
                            vinculo.principal = True
                        else:
                            vinculo.principal = item['principal']
                    
                    vinculo.save()
                    ContatoService.update(vinculo.contato, updated_by=updated_by, **item)

                else:
                    item.pop('id', None)
                    ContatoService.criar_contato_para_pessoa_juridica(
                        pessoa_juridica=pessoa,
                        created_by=updated_by,
                        **item
                    )

            for vid, vinculo in vinculos_db.items():
                if vid not in ids_recebidos:
                    # Remove o vínculo (soft delete)
                    vinculo.delete(user=updated_by)

        # 4. Sincroniza Documentos
        if documentos_data is not None:
            vinculos_db = {str(v.id): v for v in pessoa.documentos_vinculados.all()}
            ids_recebidos = set()

            for item in documentos_data:
                item_id = item.get('id')

                if item_id and str(item_id) in vinculos_db:
                    ids_recebidos.add(str(item_id))
                    vinculo = vinculos_db[str(item_id)]

                    if 'principal' in item:
                        if item['principal'] and not vinculo.principal:
                            DocumentoService.set_principal_pessoa_juridica(vinculo=vinculo, updated_by=updated_by)
                        else:
                            vinculo.principal = item['principal']
                            vinculo.save()
                    
                    DocumentoService.update(vinculo.documento, updated_by=updated_by, **item)
                
                else:
                    item.pop('id', None)
                    DocumentoService.add_documento_to_pessoa_juridica(
                        pessoa_juridica=pessoa,
                        created_by=updated_by,
                        **item
                    )

            for vid, vinculo in vinculos_db.items():
                if vid not in ids_recebidos:
                    DocumentoService.remove_vinculo_pessoa_juridica(vinculo, user=updated_by)

        # 5. Sincroniza Anexos (Lógica Simplificada para GFK)
        if anexos_data is not None:
            # Anexos não têm tabela de vínculo explícita neste modelo (usam GFK na tabela Anexo)
            # Precisamos buscar os anexos que apontam para esta PJ
            anexos_db = {str(a.id): a for a in AnexoService.get_anexos_por_entidade(pessoa)}
            ids_recebidos = set()

            for item in anexos_data:
                item_id = item.get('id')
                
                if item_id and str(item_id) in anexos_db:
                    ids_recebidos.add(str(item_id))
                    anexo = anexos_db[str(item_id)]
                    AnexoService.update(anexo, updated_by=updated_by, **item)
                else:
                    item.pop('id', None)
                    AnexoService.create(
                        entidade=pessoa,
                        created_by=updated_by,
                        **item
                    )
            
            for aid, anexo in anexos_db.items():
                if aid not in ids_recebidos:
                    AnexoService.delete(anexo, user=updated_by)

        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaJuridica, user=None) -> None:
        """Soft delete de uma Pessoa Jurídica."""
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaJuridica, user=None) -> PessoaJuridica:
        """Restaura uma Pessoa Jurídica excluída."""
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cnpj(cnpj: str) -> Optional[PessoaJuridica]:
        """Busca Pessoa Jurídica por CNPJ."""
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        return PessoaJuridica.objects.filter(
            cnpj=cnpj_limpo,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_or_create_by_cnpj(
        cnpj: str,
        created_by=None,
        **defaults
    ) -> tuple[PessoaJuridica, bool]:
        """
        Busca ou cria Pessoa Jurídica por CNPJ.
        Retorna tuple (pessoa, created).
        Lança ValidationError se CNPJ já existir.
        """
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
