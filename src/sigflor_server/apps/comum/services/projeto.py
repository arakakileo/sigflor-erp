from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import Projeto, StatusProjeto
from apps.autenticacao.models import Usuario

class ProjetoService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        descricao: str,
        filial,
        **kwargs
    ) -> Projeto:
        
        filial_id = getattr(filial, 'id', filial)

        projeto = Projeto(
            descricao=descricao,
            filial_id=filial_id,
            created_by=user,
            **kwargs
        )
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
        
        if 'filial' in kwargs:
            nova_filial = kwargs.pop('filial')
            projeto.filial_id = getattr(nova_filial, 'id', nova_filial)

        for attr, value in kwargs.items():
            if hasattr(projeto, attr):
                setattr(projeto, attr, value)
        
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def delete(*, user: Usuario, projeto: Projeto) -> None:
        # Muda status para cancelado antes de deletar logicamente?
        # Ou apenas marca deleted_at. Vamos manter simples:
        projeto.delete(user=user)

    @staticmethod
    @transaction.atomic
    def planejar(projeto: Projeto, user: Usuario) -> Projeto:
        """
        Altera o status para PLANEJADO.
        Regra: Não pode voltar para planejado se já estiver Concluído ou Cancelado.
        """
        if projeto.status in [StatusProjeto.CONCLUIDO, StatusProjeto.CANCELADO]:
            raise ValidationError(
                f"Não é possível redefinir para 'Planejado' um projeto que já está {projeto.get_status_display()}."
            )

        projeto.status = StatusProjeto.PLANEJADO
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def iniciar(projeto: Projeto, user: Usuario) -> Projeto:
        """
        Altera o status para EM_EXECUCAO.
        Regra: Não pode iniciar um projeto Cancelado ou Concluído.
        """
        if projeto.status == StatusProjeto.CANCELADO:
            raise ValidationError("Não é possível iniciar um projeto cancelado.")
        
        if projeto.status == StatusProjeto.CONCLUIDO:
            raise ValidationError("O projeto já foi concluído.")

        projeto.status = StatusProjeto.EM_EXECUCAO
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def concluir(projeto: Projeto, user: Usuario) -> Projeto:
        """
        Altera o status para CONCLUIDO.
        Regra: Não pode concluir um projeto Cancelado.
        """
        if projeto.status == StatusProjeto.CANCELADO:
            raise ValidationError("Não é possível concluir um projeto que está cancelado.")

        projeto.status = StatusProjeto.CONCLUIDO
        projeto.updated_by = user
        projeto.save()
        return projeto

    @staticmethod
    @transaction.atomic
    def cancelar(projeto: Projeto, user: Usuario) -> Projeto:
        """
        Altera o status para CANCELADO.
        Regra: Não pode cancelar um projeto Concluído.
        """
        if projeto.status == StatusProjeto.CONCLUIDO:
            raise ValidationError("Não é possível cancelar um projeto já concluído.")

        projeto.status = StatusProjeto.CANCELADO
        projeto.updated_by = user
        projeto.save()
        return projeto
