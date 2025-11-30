from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import PessoaJuridica, SituacaoCadastral


class PessoaJuridicaService:
    """Service layer para operações com Pessoa Jurídica."""

    @staticmethod
    @transaction.atomic
    def create(
        *,
        razao_social: str,
        cnpj: str,
        nome_fantasia: Optional[str] = None,
        inscricao_estadual: Optional[str] = None,
        data_abertura=None,
        situacao_cadastral: str = SituacaoCadastral.ATIVA,
        observacoes: Optional[str] = None,
        created_by=None,
    ) -> PessoaJuridica:
        """Cria uma nova Pessoa Jurídica."""
        pessoa = PessoaJuridica(
            razao_social=razao_social,
            cnpj=cnpj,
            nome_fantasia=nome_fantasia,
            inscricao_estadual=inscricao_estadual,
            data_abertura=data_abertura,
            situacao_cadastral=situacao_cadastral,
            observacoes=observacoes,
            created_by=created_by,
        )
        pessoa.save()
        return pessoa

    @staticmethod
    @transaction.atomic
    def update(pessoa: PessoaJuridica, updated_by=None, **kwargs) -> PessoaJuridica:
        """Atualiza uma Pessoa Jurídica."""
        allowed_fields = [
            'razao_social', 'nome_fantasia', 'inscricao_estadual',
            'data_abertura', 'situacao_cadastral', 'observacoes'
        ]
        for attr, value in kwargs.items():
            if attr in allowed_fields and hasattr(pessoa, attr):
                setattr(pessoa, attr, value)
        pessoa.updated_by = updated_by
        pessoa.save()
        return pessoa

    @staticmethod
    @transaction.atomic
    def delete(pessoa: PessoaJuridica, user=None) -> None:
        """Soft delete de uma Pessoa Jurídica."""
        pessoa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(pessoa: PessoaJuridica, user=None) -> PessoaJuridica:
        """Restaura uma Pessoa Jurídica excluída."""
        pessoa.restore(user=user)
        return pessoa

    @staticmethod
    def get_by_cnpj(cnpj: str) -> Optional[PessoaJuridica]:
        """Busca Pessoa Jurídica por CNPJ."""
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        return PessoaJuridica.objects.filter(
            cnpj=cnpj_limpo,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def get_or_create_by_cnpj(
        cnpj: str,
        created_by=None,
        **defaults
    ) -> tuple[PessoaJuridica, bool]:
        """
        Busca ou cria Pessoa Jurídica por CNPJ.
        Retorna tuple (pessoa, created).
        Lança ValidationError se CNPJ já existir.
        """
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        pessoa = PessoaJuridicaService.get_by_cnpj(cnpj_limpo)
        if pessoa:
            raise ValidationError({
                'cnpj': "Esta Pessoa Jurídica já está cadastrada no sistema."
            })

        defaults['cnpj'] = cnpj_limpo
        defaults['created_by'] = created_by
        return PessoaJuridicaService.create(**defaults), True
