from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models.usuarios import Usuario

from ..models import Cliente
from .pessoa_juridica import PessoaJuridicaService


class ClienteService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user:Usuario,
        pessoa_juridica_data: dict,
        descricao: str = '',
        ativo: bool = True,
        empresa_gestora,
        **kwargs
    ) -> Cliente:
        
        cnpj = pessoa_juridica_data.pop('cnpj')

        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=user,
            **pessoa_juridica_data
        )

        if hasattr(pessoa_juridica, 'cliente') and pessoa_juridica.cliente:
            raise ValidationError("Esta Pessoa Jurídica já está cadastrada como Cliente.")

        cliente = Cliente(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativo=ativo,
            empresa_gestora=empresa_gestora,
            created_by=user,
        )
        cliente.save()
        return cliente

    @staticmethod
    @transaction.atomic
    def update(cliente: Cliente, updated_by:Usuario, **kwargs) -> Cliente:
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        for attr, value in kwargs.items():
            if hasattr(cliente, attr):
                setattr(cliente, attr, value)
        cliente.updated_by = updated_by
        cliente.save()

        if pessoa_juridica_data:
            PessoaJuridicaService.update(
                pessoa=cliente.pessoa_juridica,
                updated_by=updated_by,
                **pessoa_juridica_data
            )

        return cliente

    @staticmethod
    @transaction.atomic
    def delete(cliente: Cliente, user: Usuario) -> None:
        pessoa_juridica = cliente.pessoa_juridica
        cliente.delete(user=user)
        if pessoa_juridica:
            PessoaJuridicaService.delete(pessoa_juridica, user=user)

    @staticmethod
    @transaction.atomic
    def restore(cliente: Cliente, user: Usuario) -> Cliente:
        cliente.restore(user=user)
        if cliente.pessoa_juridica:
            PessoaJuridicaService.restore(cliente.pessoa_juridica, user=user)
        return cliente

    @staticmethod
    @transaction.atomic
    def ativar(cliente: Cliente, updated_by:Usuario) -> Cliente:
        cliente.ativo = True
        cliente.updated_by = updated_by
        cliente.save()
        return cliente

    @staticmethod
    @transaction.atomic
    def desativar(cliente: Cliente, updated_by:Usuario) -> Cliente:
        cliente.ativo = False
        cliente.updated_by = updated_by
        cliente.save()
        return cliente
