# -*- coding: utf-8 -*-
from django.db import transaction
from django.utils import timezone

from ..models import Projeto
from apps.autenticacao.models import Usuario

class ProjetoService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        nome: str,
        filial,
        **kwargs
    ) -> Projeto:
        """
        Cria um novo projeto vinculado a uma filial.
        """
        
        # Garante que 'filial' seja tratado corretamente (ID ou Objeto)
        filial_id = getattr(filial, 'id', filial)

        projeto = Projeto(
            nome=nome,
            filial_id=filial_id,
            created_by=user,
            **kwargs
        )
        
        # Validações extras podem ser feitas aqui antes de salvar
        projeto.full_clean()
        projeto.save()

        return projeto

    @staticmethod
    @transaction.atomic
    def update(
        *,
        user: Usuario,
        projeto: Projeto,
        **kwargs
    ) -> Projeto:
        """
        Atualiza dados do projeto.
        """
        
        # Se estiver trocando a filial do projeto
        if 'filial' in kwargs:
            nova_filial = kwargs.pop('filial')
            projeto.filial_id = getattr(nova_filial, 'id', nova_filial)

        for attr, value in kwargs.items():
            if hasattr(projeto, attr):
                setattr(projeto, attr, value)
        
        projeto.updated_by = user
        projeto.full_clean()
        projeto.save()

        return projeto

    @staticmethod
    @transaction.atomic
    def delete(*, user: Usuario, projeto: Projeto) -> None:
        """
        Realiza o Soft Delete do projeto.
        """
        # Regra de Negócio: Não pode excluir projeto com funcionários ativos?
        # A validação de ProtectedError do Django já deve barrar se houver FK protegida,
        # mas podemos verificar alocações ativas aqui se necessário.
        
        projeto.deleted_at = timezone.now()
        projeto.ativo = False
        projeto.updated_by = user
        projeto.save()

    @staticmethod
    @transaction.atomic
    def ativar(*, user: Usuario, projeto: Projeto) -> Projeto:
        projeto.ativo = True
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def desativar(*, user: Usuario, projeto: Projeto) -> Projeto:
        # Opcional: Validar se existem alocações ativas antes de desativar
        projeto.ativo = False
        projeto.updated_by = user
        projeto.save()
        return projeto