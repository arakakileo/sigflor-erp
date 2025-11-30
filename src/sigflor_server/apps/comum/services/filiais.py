# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from ..models import Filial, Empresa
from apps.comum.models.usuarios import Usuario # Importando Usuario para type hinting


class FilialService:
    """Service layer para operações com Filial."""

    @staticmethod
    def _check_filial_ownership_access(user: Usuario, filial: Filial):
        """
        Verifica se o usuário tem acesso à filial específica. Superusuários sempre têm acesso.
        """
        if user.is_superuser:
            return True
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
        return True

    @staticmethod
    @transaction.atomic
    def create(
        *, user: Usuario, nome: str, codigo_interno: str, empresa: Optional[Empresa] = None,
        status: str = Filial.Status.ATIVA, descricao: Optional[str] = None,
        created_by=None,
    ) -> Filial:
        """Cria uma nova Filial, verificando permissão genérica para criação.
        A verificação de permissão genérica será tratada na camada de View.
        """
        # Nenhuma verificação de filial aqui para criação, pois o usuário pode estar criando uma nova filial.
        # A permissão para criar (comum_filial_editar) será verificada na View.

        filial = Filial(
            nome=nome,
            codigo_interno=codigo_interno,
            empresa=empresa,
            status=status,
            descricao=descricao,
            created_by=created_by,
        )
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def update(filial: Filial, user: Usuario, updated_by=None, **kwargs) -> Filial:
        """Atualiza uma Filial existente, verificando permissão regional."""
        FilialService._check_filial_ownership_access(user, filial)

        for attr, value in kwargs.items():
            if hasattr(filial, attr):
                setattr(filial, attr, value)
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def delete(filial: Filial, user: Usuario) -> None:
        """Soft delete de uma Filial, verificando permissão regional."""
        FilialService._check_filial_ownership_access(user, filial)
        filial.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(filial: Filial, user: Usuario, updated_by=None) -> Filial:
        """Ativa uma filial, verificando permissão regional."""
        FilialService._check_filial_ownership_access(user, filial)
        filial.status = Filial.Status.ATIVA
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def desativar(filial: Filial, user: Usuario, updated_by=None) -> Filial:
        """Desativa uma filial, verificando permissão regional."""
        FilialService._check_filial_ownership_access(user, filial)
        filial.status = Filial.Status.INATIVA
        filial.updated_by = updated_by
        filial.save()
        return filial

    @staticmethod
    @transaction.atomic
    def suspender(filial: Filial, user: Usuario, updated_by=None) -> Filial:
        """Suspende uma filial, verificando permissão regional."""
        FilialService._check_filial_ownership_access(user, filial)
        filial.status = Filial.Status.SUSPENSA
        filial.updated_by = updated_by
        filial.save()
        return filial
