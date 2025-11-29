from apps.comum.models import Exame
from django.db import transaction


class ExameService:
    """
    Serviço para gerenciar a lógica de negócio relacionada a Exames.
    """

    @staticmethod
    def create_exame(*, nome: str) -> Exame:
        """
        Cria um novo Exame.
        """
        with transaction.atomic():
            exame = Exame.objects.create(nome=nome)
        return exame

    @staticmethod
    def update_exame(*, instance: Exame, nome: str = None) -> Exame:
        """
        Atualiza um Exame existente.
        """
        with transaction.atomic():
            if nome is not None:
                instance.nome = nome
            instance.save()
        return instance

    @staticmethod
    def delete_exame(*, instance: Exame):
        """
        Realiza o soft delete de um exame.
        """
        with transaction.atomic():
            instance.soft_delete()

