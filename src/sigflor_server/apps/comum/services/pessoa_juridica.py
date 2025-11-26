from typing import Optional, List
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PessoaJuridica, Endereco, Contato, Documento, Anexo

from .enderecos import EnderecoService
from .contatos import ContatoService
from .documentos import DocumentoService
from .anexos import AnexoService
from .utils import ServiceUtils


class PessoaJuridicaService:
    """Service layer para operações com Pessoa Jurídica."""

    @staticmethod
    @transaction.atomic
    def create(
        razao_social: str,
        cnpj: str,
        nome_fantasia: Optional[str] = None,
        inscricao_estadual: Optional[str] = None,
        inscricao_municipal: Optional[str] = None,
        porte: Optional[str] = None,
        natureza_juridica: Optional[str] = None,
        data_abertura=None,
        atividade_principal: Optional[str] = None,
        atividades_secundarias: Optional[list] = None,
        situacao_cadastral: str = 'ativa',
        observacoes: Optional[str] = None,
        created_by=None,
        enderecos: List[dict] = [],
        contatos: List[dict] = [],
        documentos: List[dict] = [],
        anexos: List[dict] = [],
    ) -> PessoaJuridica:
        """Cria uma nova Pessoa Jurídica e suas entidades relacionadas."""
        pessoa = PessoaJuridica(
            razao_social=razao_social,
            cnpj=cnpj,
            nome_fantasia=nome_fantasia,
            inscricao_estadual=inscricao_estadual,
            inscricao_municipal=inscricao_municipal,
            porte=porte,
            natureza_juridica=natureza_juridica,
            data_abertura=data_abertura,
            atividade_principal=atividade_principal,
            atividades_secundarias=atividades_secundarias or [],
            situacao_cadastral=situacao_cadastral,
            observacoes=observacoes,
            created_by=created_by,
        )
        pessoa.save()

        if enderecos:
            for end_data in enderecos:
                EnderecoService.create(entidade=pessoa, created_by=created_by, **end_data)
        
        if contatos:
            for ctt_data in contatos:
                ContatoService.create(entidade=pessoa, created_by=created_by, **ctt_data)

        if documentos:
            for doc_data in documentos:
                DocumentoService.create(entidade=pessoa, created_by=created_by, **doc_data)

        if anexos:
            for anx_data in anexos:
                AnexoService.create(entidade=pessoa, created_by=created_by, **anx_data)

        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaJuridica, updated_by=None, **kwargs) -> PessoaJuridica:
        """Atualiza uma Pessoa Jurídica e sincroniza suas listas aninhadas."""
        
        # 1. Extrair as listas do payload
        # Se não vierem no payload (None), o ServiceUtils vai ignorar.
        # Se vierem vazias ([]), o ServiceUtils vai apagar tudo.
        enderecos = kwargs.pop('enderecos', None)
        contatos = kwargs.pop('contatos', None)
        documentos = kwargs.pop('documentos', None)
        anexos = kwargs.pop('anexos', None)

        # 2. Atualizar dados da própria pessoa jurídica
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
    def _atualizar_lista_aninhada(entidade_pai, dados_lista, service_filho, user):
        """
        Lógica genérica para criar, atualizar ou remover itens de uma lista.
        """

        ids_recebidos = [item.get('id') for item in dados_lista if item.get('id')]
        
        # A. REMOVER: Itens que existem no banco mas NÃO vieram na lista
        # (Isso assume que o frontend sempre manda a lista completa atualizada)
        # Para descobrir os itens atuais, usamos o método que já existe no service filho
        if service_filho == EnderecoService:
            itens_atuais = service_filho.get_enderecos_por_entidade(entidade_pai)
        elif service_filho == ContatoService:
            itens_atuais = service_filho.get_contatos_por_entidade(entidade_pai)
        elif service_filho == DocumentoService:
            itens_atuais = service_filho.get_documentos_por_entidade(entidade_pai)
        elif service_filho == AnexoService:
            itens_atuais = service_filho.get_anexos_por_entidade(entidade_pai)
        
        for item_db in itens_atuais:
            if str(item_db.id) not in ids_recebidos:
                service_filho.delete(item_db, user=user)

        # B. CRIAR ou ATUALIZAR
        for item_data in dados_lista:
            item_id = item_data.get('id')
            
            if item_id:
                # ATUALIZAR existente
                # Precisamos buscar o objeto específico. 
                # Simplificação: Assumimos que o service tem um método get ou filter
                # Num caso real, você pode otimizar buscando todos antes.
                # Aqui vou usar o model direto para exemplificar, mas o ideal é usar selector
                from ..models import Endereco, Contato
                ModelClass = Endereco if service_filho == EnderecoService else Contato
                
                try:
                    instancia = ModelClass.objects.get(pk=item_id, deleted_at__isnull=True)
                    service_filho.update(instancia, updated_by=user, **item_data)
                except ModelClass.DoesNotExist:
                    pass # Ou lançar erro
            else:
                # CRIAR novo
                service_filho.create(entidade=entidade_pai, created_by=user, **item_data)

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
    def get_or_create_by_cnpj(cnpj: str, created_by=None, **defaults) -> tuple[PessoaJuridica, bool]:
        """
        Busca ou cria Pessoa Jurídica por CNPJ.
        Nota: Se a pessoa já existir, os dados aninhados em 'defaults' serão ignorados
        nesta implementação simples, para evitar duplicidade acidental.
        """
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        pessoa = PessoaJuridicaService.get_by_cnpj(cnpj_limpo)
        if pessoa:
            # return pessoa, False
            raise ValidationError({'cnpj': "Esta Pessoa Jurídica já está cadastrada no sistema."})
        
        # Se não existe, cria usando os defaults (que podem conter enderecos, etc.)
        # O cnpj deve ser passado explicitamente para o create
        defaults['cnpj'] = cnpj_limpo
        defaults['created_by'] = created_by
        return PessoaJuridicaService.create(**defaults), True
