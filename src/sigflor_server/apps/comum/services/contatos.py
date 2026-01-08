from typing import Optional, Any, Callable
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from ..models import (
    Contato, 
    PessoaFisica, PessoaJuridica, Filial,
    PessoaFisicaContato, PessoaJuridicaContato, FilialContato
)

class ContatoService:

    @classmethod
    @transaction.atomic
    def _sincronizar_vinculos_generico(
        cls, 
        entidade_pai: Any, 
        lista_contatos: list, 
        user: Any,
        getter_func: Callable, 
        remover_func: Callable, 
        criador_func: Callable
    ):
        if lista_contatos is None:
            return

        ids_recebidos_raw = [str(item['id']) for item in lista_contatos if item.get('id')]
        
        if len(ids_recebidos_raw) != len(set(ids_recebidos_raw)):
            raise ValidationError({
                "non_field_errors": ["Não é permitido enviar o mesmo ID mais de uma vez na mesma requisição."]
            })
        
        ids_recebidos_set = set(ids_recebidos_raw)
        existentes_list = getter_func(entidade_pai)
        existentes_map = {str(v.id): v for v in existentes_list}

        cls._validar_regras_negocio(existentes_map, lista_contatos)

        for vinculo_id, vinculo in existentes_map.items():
            if vinculo_id not in ids_recebidos_set:
                remover_func(vinculo, user=user)

        for item in lista_contatos:
            item_id = str(item.get('id')) if item.get('id') else None

            if item_id and item_id not in existentes_map:
                raise ValidationError({
                    "contatos": [f"O contato com id '{item_id}' não foi encontrado ou não pertence a este registro."]
                })

            if not item_id:
                dados_create = {k:v for k,v in item.items() if k != 'id'}
                criador_func(entidade_pai, user, **dados_create)
                continue

            vinculo = existentes_map[item_id]
            cls._atualizar_vinculo_existente(vinculo, item, user)

    @classmethod
    def _validar_regras_negocio(cls, existentes_map, lista_contatos):
        """
        Valida:
        1. Duplicidade de valor/tipo.
        2. Regra de único principal.
        """
        mapa_assinaturas_banco = {}
        for v_id, v in existentes_map.items():
            sig = cls._get_assinatura_contato(obj_model=v.contato)
            mapa_assinaturas_banco[sig] = v_id

        total_principais = 0
        assinaturas_no_payload = set()

        for item in lista_contatos:
            item_id = str(item.get('id')) if item.get('id') else None

            sig_atual = cls._get_assinatura_contato(dados_dict=item)

            if sig_atual in assinaturas_no_payload:
                raise ValidationError({
                    "contatos": [f"O contato '{item.get('valor')}' foi enviado duplicado na lista."]
                })
            assinaturas_no_payload.add(sig_atual)

            if sig_atual in mapa_assinaturas_banco:
                id_dono = mapa_assinaturas_banco[sig_atual]

                is_novo = not item_id or item_id not in existentes_map
                if is_novo:
                    raise ValidationError({
                        "contatos": [f"O contato '{item.get('valor')}' já está cadastrado. Utilize o ID existente para atualizá-lo."]
                    })

                if item_id and item_id != id_dono:
                    raise ValidationError({
                        "contatos": [f"O contato '{item.get('valor')}' já existe neste cadastro."]
                    })

            eh_principal = False
            if item_id and item_id in existentes_map:
                eh_principal = item.get('principal', existentes_map[item_id].principal)
            else:
                eh_principal = item.get('principal', False)
            
            if eh_principal: 
                total_principais += 1

        if total_principais > 1:
            raise ValidationError({"contatos": ["Não é permitido ter mais de um contato marcado como principal."]})

        if total_principais == 0 and len(lista_contatos) > 0:
            raise ValidationError({"contatos": ["É obrigatório ter pelo menos um contato marcado como principal."]})

    @classmethod
    def _atualizar_vinculo_existente(cls, vinculo, item_dict, user):
        vinculo_mudou = False
        
        campos_vinculo = ['principal', 'contato_emergencia']
        
        for campo in campos_vinculo:
            if campo in item_dict and hasattr(vinculo, campo):
                valor_novo = item_dict[campo]
                if getattr(vinculo, campo) != valor_novo:
                    setattr(vinculo, campo, valor_novo)
                    vinculo_mudou = True
            
        if vinculo_mudou:
            vinculo.updated_by = user
            vinculo.save()

        contato_mudou = False
        campos_contato = ['tipo', 'valor', 'tem_whatsapp']
        
        for key in campos_contato:
            if key in item_dict and hasattr(vinculo.contato, key):
                if getattr(vinculo.contato, key) != item_dict[key]:
                    setattr(vinculo.contato, key, item_dict[key])
                    contato_mudou = True
        
        if contato_mudou:
            cls.update(vinculo.contato, updated_by=user, **item_dict)

    @staticmethod
    def _get_assinatura_contato(dados_dict: Optional[dict] = None, obj_model: Optional[Contato] = None) -> tuple:
        if obj_model:
            return (
                str(obj_model.tipo),
                str(obj_model.valor).strip().lower()
            )
        else:
            return (
                str(dados_dict.get('tipo')),
                str(dados_dict.get('valor')).strip().lower()
            )

    @staticmethod
    @transaction.atomic
    def create(
        *,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        created_by=None,
    ) -> Contato:
        contato = Contato(
            tipo=tipo,
            valor=valor,
            tem_whatsapp=tem_whatsapp,
            created_by=created_by,
        )
        contato.save()
        return contato

    @staticmethod
    @transaction.atomic
    def update(contato: Contato, updated_by=None, **kwargs) -> Contato:
        campos_permitidos = ['tipo', 'valor', 'tem_whatsapp']
        for attr, value in kwargs.items():
            if attr in campos_permitidos and hasattr(contato, attr):
                setattr(contato, attr, value)
        contato.updated_by = updated_by
        contato.save()
        return contato

    @staticmethod
    def _verificar_e_apagar_orfao(contato: Contato, user) -> None:
        if PessoaFisicaContato.objects.filter(contato=contato, deleted_at__isnull=True).exists(): return
        if PessoaJuridicaContato.objects.filter(contato=contato, deleted_at__isnull=True).exists(): return
        if FilialContato.objects.filter(contato=contato, deleted_at__isnull=True).exists(): return
        contato.delete(user=user)

    # =========================================================================
    # 1. PESSOA FÍSICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        return PessoaFisicaContato.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        contato_emergencia: bool = False,
        created_by=None,
    ) -> PessoaFisicaContato:
        
        contato = ContatoService.create(
            tipo=tipo, valor=valor, tem_whatsapp=tem_whatsapp, created_by=created_by
        )

        if principal:
            PessoaFisicaContato.objects.filter(
                pessoa_fisica=pessoa_fisica, principal=True, deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaFisicaContato(
            pessoa_fisica=pessoa_fisica,
            contato=contato,
            principal=principal,
            contato_emergencia=contato_emergencia,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)

    @classmethod
    def atualizar_contatos_pessoa_fisica(cls, pessoa_fisica, lista_contatos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=pessoa_fisica,
            lista_contatos=lista_contatos,
            user=user,
            getter_func=cls.get_contatos_pessoa_fisica,
            remover_func=cls.remove_vinculo_pessoa_fisica,
            criador_func=lambda ent, usr, **kw: cls.vincular_contato_pessoa_fisica(
                pessoa_fisica=ent, created_by=usr, **kw
            )
        )

    # =========================================================================
    # 2. PESSOA JURÍDICA (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        return PessoaJuridicaContato.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaContato:

        contato = ContatoService.create(
            tipo=tipo, valor=valor, tem_whatsapp=tem_whatsapp, created_by=created_by
        )

        if principal:
            PessoaJuridicaContato.objects.filter(
                pessoa_juridica=pessoa_juridica, principal=True, deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaJuridicaContato(
            pessoa_juridica=pessoa_juridica,
            contato=contato,
            principal=principal,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)

    @classmethod
    def atualizar_contatos_pessoa_juridica(cls, pessoa_juridica, lista_contatos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=pessoa_juridica,
            lista_contatos=lista_contatos,
            user=user,
            getter_func=cls.get_contatos_pessoa_juridica,
            remover_func=cls.remove_vinculo_pessoa_juridica,
            criador_func=lambda ent, usr, **kw: cls.vincular_contato_pessoa_juridica(
                pessoa_juridica=ent, created_by=usr, **kw
            )
        )

    # =========================================================================
    # 3. FILIAL (Gestão de Vínculos)
    # =========================================================================

    @staticmethod
    def get_contatos_filial(filial: Filial) -> QuerySet:
        return FilialContato.objects.filter(
            filial=filial,
            deleted_at__isnull=True
        ).select_related('contato').order_by('-principal', 'contato__tipo')

    @staticmethod
    @transaction.atomic
    def vincular_contato_filial(
        *,
        filial: Filial,
        tipo: str,
        valor: str,
        tem_whatsapp: bool = False,
        principal: bool = False,
        created_by=None,
    ) -> FilialContato:
        
        contato = ContatoService.create(
            tipo=tipo, valor=valor, tem_whatsapp=tem_whatsapp, created_by=created_by
        )

        if principal:
            FilialContato.objects.filter(
                filial=filial, principal=True, deleted_at__isnull=True
            ).update(principal=False)

        vinculo = FilialContato(
            filial=filial,
            contato=contato,
            principal=principal,
            created_by=created_by
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def remove_vinculo_filial(vinculo: FilialContato, user=None) -> None:
        contato = vinculo.contato
        vinculo.delete(user=user)
        ContatoService._verificar_e_apagar_orfao(contato, user)

    @classmethod
    def atualizar_contatos_filial(cls, filial, lista_contatos: list, user):
        cls._sincronizar_vinculos_generico(
            entidade_pai=filial,
            lista_contatos=lista_contatos,
            user=user,
            getter_func=cls.get_contatos_filial,
            remover_func=cls.remove_vinculo_filial,
            criador_func=lambda ent, usr, **kw: cls.vincular_contato_filial(
                filial=ent, created_by=usr, **kw
            )
        )