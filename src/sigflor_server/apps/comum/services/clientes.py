from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Cliente
from .pessoa_juridica import PessoaJuridicaService


class ClienteService:
    """Service layer para operações com Cliente."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_juridica_data: dict,
        descricao: Optional[str] = None,
        ativo: bool = True,
        created_by=None,
    ) -> Cliente:
        """Cria um novo Cliente."""
        
        cnpj = pessoa_juridica_data.pop('cnpj')

        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=created_by,
            **pessoa_juridica_data
        )

        # Validação de unicidade (Um contratante por PJ)
        if hasattr(pessoa_juridica, 'contratante') and pessoa_juridica.contratante:
            raise ValidationError("Esta Pessoa Jurídica já está cadastrada como Cliente.")

        contratante = Cliente(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativo=ativo,
            created_by=created_by,
        )
        contratante.save()
        return contratante

    @staticmethod
    @transaction.atomic
    def update(contratante: Cliente, updated_by=None, **kwargs) -> Cliente:
        """Atualiza um Cliente e seus dados vinculados de Pessoa Jurídica."""
        
        # 1. Extrair dados da Pessoa Jurídica (se houver)
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        # 2. Atualizar dados do próprio Cliente
        for attr, value in kwargs.items():
            if hasattr(contratante, attr):
                setattr(contratante, attr, value)
        contratante.updated_by = updated_by
        contratante.save()

        # 3. Delegar atualização da Pessoa Jurídica (incluindo listas aninhadas)
        if pessoa_juridica_data:
            PessoaJuridicaService.update(
                pessoa=contratante.pessoa_juridica,
                updated_by=updated_by,
                **pessoa_juridica_data
            )

        return contratante

    @staticmethod
    @transaction.atomic
    def delete(contratante: Cliente, user=None) -> None:
        """Soft delete de um Cliente."""
        contratante.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(contratante: Cliente, updated_by=None) -> Cliente:
        """Ativa um contratante."""
        contratante.ativo = True
        contratante.updated_by = updated_by
        contratante.save()
        return contratante

    @staticmethod
    @transaction.atomic
    def desativar(contratante: Cliente, updated_by=None) -> Cliente:
        """Desativa um contratante."""
        contratante.ativo = False
        contratante.updated_by = updated_by
        contratante.save()
        return contratante
