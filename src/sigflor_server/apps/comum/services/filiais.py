# -*- coding: utf-8 -*-
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from ..models import Filial
from ..models.enums import StatusFilial
from .enderecos import EnderecoService
from .contatos import ContatoService
from .utils import ServiceUtils
from apps.autenticacao.models.usuarios import Usuario


class FilialService:

    @staticmethod
    def _verificar_acesso_filial(user: Usuario, filial: Filial):
        if user.is_superuser:
            return True
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
        return True

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        nome: str,
        codigo_interno: str,
        enderecos: list,
        contatos: list,
        status: str = StatusFilial.ATIVA,
        descricao: str = '',
        empresa=None,
        **kwargs
    ) -> Filial:

        filial = Filial(
            nome=nome,
            codigo_interno=codigo_interno,
            empresa=empresa,
            status=status,
            descricao=descricao,
            created_by=user,
        )
        filial.save()

        if enderecos:
            for dados_endereco in enderecos:
                EnderecoService.vincular_endereco_filial(
                    filial=filial,
                    created_by=user,
                    **dados_endereco
                )

        if contatos:
            for dados_contato in contatos:
                ContatoService.vincular_contato_filial(
                    filial=filial,
                    created_by=user,
                    **dados_contato
                )

        return filial

    @staticmethod
    @transaction.atomic
    def update(filial: Filial, user: Usuario, **kwargs) -> Filial:

        FilialService._verificar_acesso_filial(user, filial)

        enderecos = kwargs.pop('enderecos', None)
        contatos = kwargs.pop('contatos', None)

        for attr, value in kwargs.items():
            if hasattr(filial, attr):
                setattr(filial, attr, value)
        
        filial.updated_by = user
        filial.save()

        if enderecos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=filial,
                dados_lista=enderecos,
                service_filho=EnderecoService,
                user=user,
                metodo_busca_existentes='get_enderecos_filial', #
                metodo_criar='criar_endereco_filial',           #
                campo_entidade_pai='filial'
            )

        if contatos is not None:
            ServiceUtils.sincronizar_lista_aninhada(
                entidade_pai=filial,
                dados_lista=contatos,
                service_filho=ContatoService,
                user=user,
                metodo_busca_existentes='get_contatos_filial',
                metodo_criar='criar_contato_filial',
            )

        return filial

    @staticmethod
    @transaction.atomic
    def delete(filial: Filial, user: Usuario) -> None:
        FilialService._verificar_acesso_filial(user, filial)
        filial.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(filial: Filial, user: Usuario) -> Filial:
        FilialService._verificar_acesso_filial(user, filial)
        filial.status = StatusFilial.ATIVA
        filial.updated_by = user
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def desativar(filial: Filial, user: Usuario) -> Filial:
        FilialService._verificar_acesso_filial(user, filial)
        filial.status = StatusFilial.INATIVA
        filial.updated_by = user
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def suspender(filial: Filial, user: Usuario) -> Filial:
        FilialService._verificar_acesso_filial(user, filial)
        filial.status = StatusFilial.SUSPENSA
        filial.updated_by = user
        filial.save()
        return filial
