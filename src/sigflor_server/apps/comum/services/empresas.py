from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Empresa
from .pessoa_juridica import PessoaJuridicaService
from apps.autenticacao.models.usuarios import Usuario

class EmpresaService:

    @staticmethod
    @transaction.atomic
    def create(
        *, 
        user: Usuario, 
        pessoa_juridica_data: dict,
        descricao: str = '',
        ativa: bool = True,
        **kwargs
    ) -> Empresa:
        
        cnpj = pessoa_juridica_data.pop('cnpj')
        
        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=user,
            **pessoa_juridica_data 
        )

        if hasattr(pessoa_juridica, 'empresa') and pessoa_juridica.empresa:
            raise ValidationError("Esta Pessoa Jurídica já está vinculada a uma Empresa do grupo.")

        empresa = Empresa(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativa=ativa,
            created_by=user,
        )
        empresa.save()
        return empresa

    @staticmethod
    @transaction.atomic
    def update(empresa: Empresa, updated_by:Usuario, **kwargs) -> Empresa:
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        for attr, value in kwargs.items():
            if hasattr(empresa, attr):
                setattr(empresa, attr, value)
        empresa.updated_by = updated_by
        empresa.save()

        if pessoa_juridica_data:
            PessoaJuridicaService.update(
                pessoa=empresa.pessoa_juridica,
                updated_by=updated_by,
                **pessoa_juridica_data
            )

        return empresa

    @staticmethod
    @transaction.atomic
    def delete(empresa: Empresa, user: Usuario) -> None:
        pessoa_juridica = empresa.pessoa_juridica
        empresa.delete(user=user)
        if pessoa_juridica:
            PessoaJuridicaService.delete(pessoa_juridica, user=user)

    @staticmethod
    @transaction.atomic
    def restore(empresa: Empresa, user: Usuario) -> Empresa:
        empresa.restore(user=user)
        if empresa.pessoa_juridica:
            PessoaJuridicaService.restore(empresa.pessoa_juridica, user=user)
        return empresa

    @staticmethod
    @transaction.atomic
    def ativar(empresa: Empresa, updated_by:Usuario) -> Empresa:
        empresa.ativa = True
        empresa.updated_by = updated_by
        empresa.save()
        return empresa

    @staticmethod
    @transaction.atomic
    def desativar(empresa: Empresa, updated_by:Usuario) -> Empresa:
        empresa.ativa = False
        empresa.updated_by = updated_by
        empresa.save()
        return empresa