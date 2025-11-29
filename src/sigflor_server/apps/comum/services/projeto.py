from apps.comum.models import Projeto, Contratante, Filial
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from apps.comum.models.usuarios import Usuario # Importando Usuario para type hinting


class ProjetoService:
    """
    Serviço para gerenciar a lógica de negócio relacionada a Projetos.
    """

    @staticmethod
    def _check_filial_access(user: Usuario, filial: Filial):
        """
        Verifica se o usuário tem acesso à filial. Superusuários sempre têm acesso.
        """
        if user.is_superuser:
            return True
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
        return True

    @staticmethod
    def create_projeto(
        *, user: Usuario, nome: str, cliente: Contratante, filial: Filial
    ) -> Projeto:
        """
        Cria um novo Projeto, verificando permissão regional.
        A empresa do projeto é definida automaticamente a partir do cliente.
        """
        ProjetoService._check_filial_access(user, filial)

        with transaction.atomic():
            projeto = Projeto.objects.create(
                nome=nome,
                cliente=cliente,
                filial=filial,
            )
        return projeto

    @staticmethod
    def update_projeto(
        *, user: Usuario, instance: Projeto, nome: str = None, cliente: Contratante = None, filial: Filial = None
    ) -> Projeto:
        """
        Atualiza um Projeto existente, verificando permissão regional.
        """
        ProjetoService._check_filial_access(user, instance.filial) # Verifica a filial atual do projeto
        if filial and filial != instance.filial: # Se a filial estiver sendo alterada, verifica a nova filial
            ProjetoService._check_filial_access(user, filial)

        with transaction.atomic():
            if nome is not None:
                instance.nome = nome
            if cliente is not None:
                instance.cliente = cliente
            if filial is not None:
                instance.filial = filial
            instance.save()
        return instance

    @staticmethod
    def delete_projeto(*, user: Usuario, instance: Projeto):
        """
        Realiza o soft delete de um projeto, verificando permissão regional.
        """
        ProjetoService._check_filial_access(user, instance.filial)

        with transaction.atomic():
            instance.soft_delete()
