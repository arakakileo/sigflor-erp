from typing import Optional
from django.db import transaction

from ..models import Contratante, PessoaJuridica
from .pessoa_juridica import PessoaJuridicaService


class ContratanteService:
    """Service layer para operações com Contratante."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_juridica_data: dict,
        descricao: Optional[str] = None,
        ativo: bool = True,
        created_by=None,
    ) -> Contratante:
        """Cria um novo Contratante."""
        # Cria ou obtém a PessoaJuridica
        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=pessoa_juridica_data.get('cnpj'),
            razao_social=pessoa_juridica_data.get('razao_social'),
            nome_fantasia=pessoa_juridica_data.get('nome_fantasia'),
            created_by=created_by,
        )

        contratante = Contratante(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativo=ativo,
            created_by=created_by,
        )
        contratante.save()
        return contratante

    @staticmethod
    @transaction.atomic
    def update(contratante: Contratante, updated_by=None, **kwargs) -> Contratante:
        """Atualiza um Contratante existente."""
        for attr, value in kwargs.items():
            if hasattr(contratante, attr):
                setattr(contratante, attr, value)
        contratante.updated_by = updated_by
        contratante.save()
        return contratante

    @staticmethod
    @transaction.atomic
    def delete(contratante: Contratante, user=None) -> None:
        """Soft delete de um Contratante."""
        contratante.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(contratante: Contratante, updated_by=None) -> Contratante:
        """Ativa um contratante."""
        contratante.ativo = True
        contratante.updated_by = updated_by
        contratante.save()
        return contratante

    @staticmethod
    @transaction.atomic
    def desativar(contratante: Contratante, updated_by=None) -> Contratante:
        """Desativa um contratante."""
        contratante.ativo = False
        contratante.updated_by = updated_by
        contratante.save()
        return contratante
