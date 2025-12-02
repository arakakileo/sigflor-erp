from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Empresa
from .pessoa_juridica import PessoaJuridicaService


class EmpresaService:
    """Service layer para operações com Empresa."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_juridica_data: dict,
        descricao: Optional[str] = None,
        ativa: bool = True,
        created_by=None,
    ) -> Empresa:
        """Cria uma nova Empresa."""

        # O get_or_create agora sabe lidar com os dados aninhados dentro de 'defaults'
        # passamos todo o resto do dicionário como kwargs
        cnpj = pessoa_juridica_data.pop('cnpj')
        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=created_by,
            **pessoa_juridica_data 
        )

        # Verifica se essa PJ já está vinculada a outra Empresa (regra de unicidade 1:1)
        if hasattr(pessoa_juridica, 'empresa') and pessoa_juridica.empresa:
            raise ValidationError("Esta Pessoa Jurídica já está vinculada a uma Empresa do grupo.")

        empresa = Empresa(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativa=ativa,
            created_by=created_by,
        )
        empresa.save()
        return empresa

    @staticmethod
    @transaction.atomic
    def update(empresa: Empresa, updated_by=None, **kwargs) -> Empresa:
        """Atualiza uma Empresa e seus dados vinculados de Pessoa Jurídica."""
        
        # 1. Extrair dados da Pessoa Jurídica (se houver)
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        for attr, value in kwargs.items():
            if hasattr(empresa, attr):
                setattr(empresa, attr, value)
        empresa.updated_by = updated_by
        empresa.save()
        # 3. Delegar atualização da Pessoa Jurídica (incluindo listas aninhadas)
        if pessoa_juridica_data:
            PessoaJuridicaService.update(
                pessoa=empresa.pessoa_juridica,
                updated_by=updated_by,
                **pessoa_juridica_data
            )

        return empresa

    @staticmethod
    @transaction.atomic
    def delete(empresa: Empresa, user=None) -> None:
        """Soft delete de uma Empresa."""
        empresa.delete(user=user)
