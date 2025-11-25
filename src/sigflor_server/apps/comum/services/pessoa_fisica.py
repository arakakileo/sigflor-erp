from typing import Optional
from django.db import transaction

from ..models import PessoaFisica


class PessoaFisicaService:
    """Service layer para operações com Pessoa Física."""

    @staticmethod
    @transaction.atomic
    def create(
        nome_completo: str,
        cpf: str,
        rg: Optional[str] = None,
        orgao_emissor: Optional[str] = None,
        data_nascimento=None,
        sexo: Optional[str] = None,
        estado_civil: Optional[str] = None,
        nacionalidade: Optional[str] = None,
        naturalidade: Optional[str] = None,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> PessoaFisica:
        """Cria uma nova Pessoa Física."""
        pessoa = PessoaFisica(
            nome_completo=nome_completo,
            cpf=cpf,
            rg=rg,
            orgao_emissor=orgao_emissor,
            data_nascimento=data_nascimento,
            sexo=sexo,
            estado_civil=estado_civil,
            nacionalidade=nacionalidade,
            naturalidade=naturalidade,
            observacoes=observacoes,
            created_by=created_by,
        )
        pessoa.save()
        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaFisica, updated_by=None, **kwargs) -> PessoaFisica:
        """Atualiza uma Pessoa Física existente."""
        for attr, value in kwargs.items():
            if hasattr(pessoa, attr):
                setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()
        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaFisica, user=None) -> None:
        """Soft delete de uma Pessoa Física."""
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaFisica, user=None) -> PessoaFisica:
        """Restaura uma Pessoa Física excluída."""
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cpf(cpf: str) -> Optional[PessoaFisica]:
        """Busca Pessoa Física por CPF."""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        return PessoaFisica.objects.filter(
            cpf=cpf_limpo,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_or_create_by_cpf(cpf: str, **defaults) -> tuple[PessoaFisica, bool]:
        """Busca ou cria Pessoa Física por CPF."""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        pessoa = PessoaFisicaService.get_by_cpf(cpf_limpo)
        if pessoa:
            return pessoa, False
        return PessoaFisicaService.create(cpf=cpf_limpo, **defaults), True
