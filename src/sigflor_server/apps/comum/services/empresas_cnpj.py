from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import EmpresaCNPJ, PessoaJuridica
from .pessoa_juridica import PessoaJuridicaService


class EmpresaCNPJService:
    """Service layer para operações com EmpresaCNPJ."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_juridica_data: dict,
        descricao: Optional[str] = None,
        ativa: bool = True,
        matriz: bool = False,
        created_by=None,
    ) -> EmpresaCNPJ:
        """Cria uma nova EmpresaCNPJ."""
        # Verifica se já existe matriz e impede criar outra
        if matriz and EmpresaCNPJ.objects.filter(matriz=True, deleted_at__isnull=True).exists():
            raise ValidationError("Já existe uma empresa matriz cadastrada.")

        # Cria ou obtém a PessoaJuridica
        pessoa_juridica, _ = PessoaJuridicaService.get_or_create_by_cnpj(
            cnpj=pessoa_juridica_data.get('cnpj'),
            razao_social=pessoa_juridica_data.get('razao_social'),
            nome_fantasia=pessoa_juridica_data.get('nome_fantasia'),
            created_by=created_by,
        )

        empresa = EmpresaCNPJ(
            pessoa_juridica=pessoa_juridica,
            descricao=descricao,
            ativa=ativa,
            matriz=matriz,
            created_by=created_by,
        )
        empresa.save()
        return empresa

    @staticmethod
    @transaction.atomic
    def update(empresa: EmpresaCNPJ, updated_by=None, **kwargs) -> EmpresaCNPJ:
        """Atualiza uma EmpresaCNPJ existente."""
        # Se está tornando matriz, remove matriz anterior
        if kwargs.get('matriz') and not empresa.matriz:
            EmpresaCNPJ.objects.filter(
                matriz=True,
                deleted_at__isnull=True
            ).exclude(pk=empresa.pk).update(matriz=False)

        for attr, value in kwargs.items():
            if hasattr(empresa, attr):
                setattr(empresa, attr, value)
        empresa.updated_by = updated_by
        empresa.save()
        return empresa

    @staticmethod
    @transaction.atomic
    def delete(empresa: EmpresaCNPJ, user=None) -> None:
        """Soft delete de uma EmpresaCNPJ."""
        empresa.delete(user=user)

    @staticmethod
    @transaction.atomic
    def tornar_matriz(empresa: EmpresaCNPJ, updated_by=None) -> EmpresaCNPJ:
        """Define uma empresa como matriz (remove flag das outras)."""
        EmpresaCNPJ.objects.filter(
            matriz=True,
            deleted_at__isnull=True
        ).update(matriz=False)
        empresa.matriz = True
        empresa.updated_by = updated_by
        empresa.save()
        return empresa
