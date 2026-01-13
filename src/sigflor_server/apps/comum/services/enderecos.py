from typing import Optional, Any, Callable
from datetime import timedelta
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from ..models import (
    Endereco, TipoEndereco,
    PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco,
    PessoaFisica, PessoaJuridica, Filial
)

class EnderecoService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        created_by=None,
    ) -> Endereco:

        endereco = Endereco(
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            created_by=created_by,
        )
        endereco.save()
        return endereco

    @staticmethod
    @transaction.atomic
    def update(endereco: Endereco, updated_by=None, **kwargs) -> Endereco:

        campos_permitidos = [
            'logradouro', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'cep', 'pais'
        ]
        for attr, value in kwargs.items():
            if attr in campos_permitidos and hasattr(endereco, attr):
                setattr(endereco, attr, value)
        
        endereco.updated_by = updated_by
        endereco.save()
        return endereco

    @staticmethod
    def _verificar_e_apagar_orfao(endereco: Endereco, user) -> None:

        if PessoaFisicaEndereco.objects.filter(endereco=endereco, deleted_at__isnull=True).exists():
            return
        
        if PessoaJuridicaEndereco.objects.filter(endereco=endereco, deleted_at__isnull=True).exists():
            return

        if FilialEndereco.objects.filter(endereco=endereco, deleted_at__isnull=True).exists():
            return

        endereco.delete(user=user)

    @classmethod
    @transaction.atomic
    def _sincronizar_vinculos_generico(
        cls, 
        entidade_pai: Any, 
        lista_enderecos: list, 
        user: Any,
        getter_func: Callable, 
        remover_func: Callable, 
        criador_func: Callable
    ):
        """
        Algoritmo genérico de sincronização de endereços.
        Funciona para qualquer entidade que tenha relacionamento N:N com Endereço
        e use tabelas intermediárias com campos 'tipo' e 'principal'.
        """
        if lista_enderecos is None:
            return

        ids_recebidos_raw = [str(item['id']) for item in lista_enderecos if item.get('id')]
        if len(ids_recebidos_raw) != len(set(ids_recebidos_raw)):
            raise ValidationError({
                "non_field_errors": ["Não é permitido enviar o mesmo ID mais de uma vez na mesma requisição."]
            })
        
        ids_recebidos_set = set(ids_recebidos_raw)
        existentes_list = getter_func(entidade_pai)
        existentes_map = {str(v.id): v for v in existentes_list}

        cls._validar_regras_negocio(existentes_map, lista_enderecos)

        for vinculo_id, vinculo in existentes_map.items():
            if vinculo_id not in ids_recebidos_set:
                remover_func(vinculo, user=user)

        for item in lista_enderecos:
            item_id = str(item.get('id')) if item.get('id') else None

            if item_id and item_id not in existentes_map:
                raise ValidationError({
                    "enderecos": [f"O endereço com id '{item_id}' não foi encontrado ou não pertence a este registro."]
                })

            if not item_id:
                dados_create = {k:v for k,v in item.items() if k != 'id'}
                criador_func(entidade_pai, user, **dados_create)
                continue

            vinculo = existentes_map[item_id]
            cls._atualizar_vinculo_existente(vinculo, item, user)

    @classmethod
    def _restaurar_vinculos_generico(
        cls, 
        model_vinculo, 
        campo_filho, 
        filtro_pai, 
        data_delecao_pai, 
        user
    ):
        if not data_delecao_pai:
            return

        margem = timedelta(seconds=5)
        inicio = data_delecao_pai - margem
        fim = data_delecao_pai + margem

        vinculos = model_vinculo.objects.filter(
            **filtro_pai,
            deleted_at__range=(inicio, fim)
        )

        for vinculo in vinculos:
            vinculo.restore(user=user)
            endereco = getattr(vinculo, campo_filho)
            if endereco.deleted_at and inicio <= endereco.deleted_at <= fim:
                endereco.restore(user=user)

    @classmethod
    def _validar_regras_negocio(cls, existentes_map, lista_enderecos):
        """
        Valida regras de consistência:
        1. Duplicidade de endereços (no payload e contra o banco).
        2. Obrigatoriedade de exatamente um endereço principal.
        """
        mapa_assinaturas_banco = {}
        
        for v_id, v in existentes_map.items():
            sig = cls._get_assinatura_enderecos(obj_model=v.endereco)
            mapa_assinaturas_banco[sig] = v_id

        total_principais = 0
        assinaturas_no_payload = set()

        for item in lista_enderecos:
            item_id = str(item.get('id')) if item.get('id') else None
            
            sig_atual = cls._get_assinatura_enderecos(dados_dict=item)
            
            if sig_atual in assinaturas_no_payload:
                raise ValidationError({
                    "enderecos": [f"O endereço '{item.get('logradouro')}' foi enviado duplicado na lista."]
                })
            assinaturas_no_payload.add(sig_atual)

            if sig_atual in mapa_assinaturas_banco:
                id_dono = mapa_assinaturas_banco[sig_atual]
                
                if not item_id:
                    raise ValidationError({
                        "enderecos": [f"O endereço '{item.get('logradouro')}' já está cadastrado. Utilize o ID existente ({id_dono}) para atualizá-lo."]
                    })
                
                if item_id and item_id != id_dono:
                    raise ValidationError({
                        "enderecos": [f"O endereço '{item.get('logradouro')}' já existe em outro cadastro desta empresa."]
                    })

            eh_principal = False
            
            if item_id and item_id in existentes_map:
                eh_principal = item.get('principal', existentes_map[item_id].principal)
            elif not item_id:
                eh_principal = item.get('principal', False)
            
            if eh_principal:
                total_principais += 1

        if total_principais > 1:
            raise ValidationError({
                "enderecos": ["Não é permitido ter mais de um endereço marcado como principal."]
            })
            
        if total_principais == 0:
            raise ValidationError({
                "enderecos": ["É obrigatório ter pelo menos um endereço marcado como principal."]
            })

    @classmethod
    def _atualizar_vinculo_existente(cls, vinculo, item_dict, user):

        vinculo_mudou = False
        
        if 'tipo' in item_dict and vinculo.tipo != item_dict['tipo']:
            vinculo.tipo = item_dict['tipo']
            vinculo_mudou = True
        
        if 'principal' in item_dict and vinculo.principal != item_dict['principal']:
            vinculo.principal = item_dict['principal']
            vinculo_mudou = True
            
        if vinculo_mudou:
            vinculo.updated_by = user
            vinculo.save()

        endereco_mudou = False
        ignorar = ['id', 'tipo', 'principal']
        
        for key, value in item_dict.items():
            if key not in ignorar and hasattr(vinculo.endereco, key):
                if getattr(vinculo.endereco, key) != value:
                    endereco_mudou = True
                    break
        
        if endereco_mudou:
            cls.update(vinculo.endereco, updated_by=user, **item_dict)

    @staticmethod
    def _get_assinatura_enderecos(dados_dict: Optional[dict] = None, obj_model: Optional[Endereco] = None) -> tuple:
        """
        Gera uma assinatura única para identificar duplicidade de endereço.
        Considera: Logradouro, Número, Complemento, Cidade, Estado e CEP.
        """
        if obj_model:
            return (
                str(obj_model.logradouro or '').strip().lower(),
                str(obj_model.numero or '').strip().lower(),
                str(obj_model.complemento or '').strip().lower(),
                str(obj_model.cidade or '').strip().lower(),
                str(obj_model.estado or '').strip().lower(),
                str(obj_model.cep or '').strip().lower(),
            )
        else:
            return (
                str(dados_dict.get('logradouro') or '').strip().lower(),
                str(dados_dict.get('numero') or '').strip().lower(),
                str(dados_dict.get('complemento') or '').strip().lower(),
                str(dados_dict.get('cidade') or '').strip().lower(),
                str(dados_dict.get('estado') or '').strip().lower(),
                str(dados_dict.get('cep') or '').strip().lower(),
            )

    # =========================================================================
    # 1. PESSOA FÍSICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_enderecos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        return PessoaFisicaEndereco.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    @transaction.atomic
    def vincular_endereco_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.RESIDENCIAL,
        principal: bool = False,
        created_by=None,
    ) -> PessoaFisicaEndereco:
        
        endereco = EnderecoService.create(
            logradouro=logradouro, numero=numero, complemento=complemento,
            bairro=bairro, cidade=cidade, estado=estado, cep=cep,
            pais=pais, created_by=created_by,
        )

        if principal:
            PessoaFisicaEndereco.objects.filter(
                pessoa_fisica=pessoa_fisica,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaFisicaEndereco(
            pessoa_fisica=pessoa_fisica,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaEndereco, user=None) -> None:
        endereco = vinculo.endereco
        vinculo.delete(user=user)
        EnderecoService._verificar_e_apagar_orfao(endereco, user)

    @classmethod
    def restaurar_enderecos_pessoa_fisica(cls, pessoa, data_delecao_pai, user):
        cls._restaurar_vinculos_generico(
            model_vinculo=PessoaFisicaEndereco,
            campo_filho='endereco',
            filtro_pai={'pessoa_fisica': pessoa},
            data_delecao_pai=data_delecao_pai,
            user=user
        )

    @classmethod
    def atualizar_enderecos_pessoa_fisica(cls, pessoa_fisica, lista_enderecos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=pessoa_fisica,
            lista_enderecos=lista_enderecos,
            user=user,
            getter_func=cls.get_enderecos_pessoa_fisica,
            remover_func=cls.remove_vinculo_pessoa_fisica,
            criador_func=lambda ent, usr, **kw: cls.vincular_endereco_pessoa_fisica(
                pessoa_fisica=ent, created_by=usr, **kw
            )
        )

    # =========================================================================
    # 2. PESSOA JURÍDICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_enderecos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        return PessoaJuridicaEndereco.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    @transaction.atomic
    def vincular_endereco_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.COMERCIAL,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaEndereco:
        
        endereco = EnderecoService.create(
            logradouro=logradouro, numero=numero, complemento=complemento,
            bairro=bairro, cidade=cidade, estado=estado, cep=cep,
            pais=pais, created_by=created_by,
        )

        if principal:
            PessoaJuridicaEndereco.objects.filter(
                pessoa_juridica=pessoa_juridica,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaJuridicaEndereco(
            pessoa_juridica=pessoa_juridica,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaEndereco, user=None) -> None:
        endereco = vinculo.endereco
        vinculo.delete(user=user)
        EnderecoService._verificar_e_apagar_orfao(endereco, user)

    @classmethod
    def restaurar_enderecos_pessoa_juridica(cls, pessoa, data_delecao_pai, user):
        cls._restaurar_vinculos_generico(
            model_vinculo=PessoaJuridicaEndereco,
            campo_filho='endereco',
            filtro_pai={'pessoa_juridica': pessoa},
            data_delecao_pai=data_delecao_pai,
            user=user
        )   

    @classmethod
    def atualizar_enderecos_pessoa_juridica(cls, pessoa_juridica, lista_enderecos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=pessoa_juridica,
            lista_enderecos=lista_enderecos,
            user=user,
            getter_func=cls.get_enderecos_pessoa_juridica,
            remover_func=cls.remove_vinculo_pessoa_juridica,
            criador_func=lambda ent, usr, **kw: cls.vincular_endereco_pessoa_juridica(
                pessoa_juridica=ent, created_by=usr, **kw
            )
        )

    # =========================================================================
    # 3. FILIAL (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_enderecos_filial(filial: Filial) -> QuerySet:
        return FilialEndereco.objects.filter(
            filial=filial,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    @transaction.atomic
    def vincular_endereco_filial(
        *,
        filial: Filial,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.COMERCIAL,
        principal: bool = False,
        created_by=None,
    ) -> FilialEndereco:
        
        endereco = EnderecoService.create(
            logradouro=logradouro, numero=numero, complemento=complemento,
            bairro=bairro, cidade=cidade, estado=estado, cep=cep,
            pais=pais, created_by=created_by,
        )

        if principal:
            FilialEndereco.objects.filter(
                filial=filial,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = FilialEndereco(
            filial=filial,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_filial(vinculo: FilialEndereco, user=None) -> None:
        endereco = vinculo.endereco
        vinculo.delete(user=user)
        EnderecoService._verificar_e_apagar_orfao(endereco, user)

    @classmethod
    def restaurar_enderecos_filial(cls, filial, data_delecao_pai, user):
        cls._restaurar_vinculos_generico(
            model_vinculo=FilialEndereco,
            campo_filho='endereco',
            filtro_pai={'filial': filial},
            data_delecao_pai=data_delecao_pai,
            user=user
        )

    @classmethod
    def atualizar_enderecos_filial(cls, filial, lista_enderecos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=filial,
            lista_enderecos=lista_enderecos,
            user=user,
            getter_func=cls.get_enderecos_filial,
            remover_func=cls.remove_vinculo_filial,
            criador_func=lambda ent, usr, **kw: cls.vincular_endereco_filial(
                filial=ent, created_by=usr, **kw
            )
        )