from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Contratante
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
        
        cnpj = pessoa_juridica_data.pop('cnpj')

        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=cnpj,
            created_by=created_by,
            **pessoa_juridica_data
        )

        # Validação de unicidade (Um contratante por PJ)
        if hasattr(pessoa_juridica, 'contratante') and pessoa_juridica.contratante:
            raise ValidationError("Esta Pessoa Jurídica já está cadastrada como Contratante.")

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
        """Atualiza um Contratante e seus dados vinculados de Pessoa Jurídica."""
        
        # 1. Extrair dados da Pessoa Jurídica (se houver)
        pessoa_juridica_data = kwargs.pop('pessoa_juridica', None)

        # 2. Atualizar dados do próprio Contratante
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
