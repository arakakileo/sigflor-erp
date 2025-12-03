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
        empresa_gestora=None,
    ) -> Cliente:
        """Cria um novo Cliente."""
        
        cnpj = pessoa_juridica_data.pop('cnpj')

        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=created_by,
            **pessoa_juridica_data
        )

        # Validação de unicidade (Um cliente por PJ)
        if hasattr(pessoa_juridica, 'cliente') and pessoa_juridica.cliente:
            raise ValidationError("Esta Pessoa Jurídica já está cadastrada como Cliente.")

        cliente = Cliente(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativo=ativo,
            empresa_gestora=empresa_gestora,
            created_by=created_by,
        )
        cliente.save()
        return cliente

    @staticmethod
    @transaction.atomic
    def update(cliente: Cliente, updated_by=None, **kwargs) -> Cliente:
        """Atualiza um Cliente e seus dados vinculados de Pessoa Jurídica."""
        
        # 1. Extrair dados da Pessoa Jurídica (se houver)
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        # 2. Atualizar dados do próprio Cliente
        for attr, value in kwargs.items():
            if hasattr(cliente, attr):
                setattr(cliente, attr, value)
        cliente.updated_by = updated_by
        cliente.save()

        # 3. Delegar atualização da Pessoa Jurídica (incluindo listas aninhadas)
        if pessoa_juridica_data:
            PessoaJuridicaService.update(
                pessoa=cliente.pessoa_juridica,
                updated_by=updated_by,
                **pessoa_juridica_data
            )

        return cliente

    @staticmethod
    @transaction.atomic
    def delete(cliente: Cliente, user=None) -> None:
        """Soft delete de um Cliente."""
        cliente.delete(user=user)

    @staticmethod
    @transaction.atomic
    def ativar(cliente: Cliente, updated_by=None) -> Cliente:
        """Ativa um cliente."""
        cliente.ativo = True
        cliente.updated_by = updated_by
        cliente.save()
        return cliente

    @staticmethod
    @transaction.atomic
    def desativar(cliente: Cliente, updated_by=None) -> Cliente:
        """Desativa um cliente."""
        cliente.ativo = False
        cliente.updated_by = updated_by
        cliente.save()
        return cliente
