# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction
from django.utils import timezone

from apps.comum.models import PessoaFisica
from ..models import Funcionario


class FuncionarioService:
    """Service layer para operacoes com Funcionario."""

    @staticmethod
    @transaction.atomic
    def create(
        pessoa_fisica_data: Optional[dict] = None,
        pessoa_fisica: Optional[PessoaFisica] = None,
        created_by=None,
        **kwargs
    ) -> Funcionario:
        """
        Cria um novo funcionario.

        Pode receber:
        - pessoa_fisica_data: dict com dados para criar nova PessoaFisica
        - pessoa_fisica: instancia existente de PessoaFisica
        """
        # Se nao tem pessoa_fisica, cria uma nova
        if not pessoa_fisica and pessoa_fisica_data:
            pessoa_fisica = PessoaFisica.objects.create(
                created_by=created_by,
                **pessoa_fisica_data
            )
        elif not pessoa_fisica:
            raise ValueError('pessoa_fisica ou pessoa_fisica_data e obrigatorio')

        # Verifica se ja existe funcionario para esta pessoa
        if Funcionario.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).exists():
            raise ValueError('Ja existe um funcionario cadastrado para esta pessoa')

        funcionario = Funcionario(
            pessoa_fisica=pessoa_fisica,
            created_by=created_by,
            **kwargs
        )
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def update(funcionario: Funcionario, updated_by=None, **kwargs) -> Funcionario:
        """Atualiza um funcionario existente."""
        for attr, value in kwargs.items():
            if hasattr(funcionario, attr):
                setattr(funcionario, attr, value)

        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def delete(funcionario: Funcionario, user=None) -> None:
        """Soft delete de um funcionario."""
        funcionario.delete(user=user)

    @staticmethod
    @transaction.atomic
    def demitir(
        funcionario: Funcionario,
        data_demissao: Optional[timezone.datetime] = None,
        updated_by=None
    ) -> Funcionario:
        """Registra demissao do funcionario."""
        funcionario.status = Funcionario.Status.DEMITIDO
        funcionario.data_demissao = data_demissao or timezone.now().date()
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def reativar(funcionario: Funcionario, updated_by=None) -> Funcionario:
        """Reativa um funcionario demitido."""
        funcionario.status = Funcionario.Status.ATIVO
        funcionario.data_demissao = None
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def afastar(
        funcionario: Funcionario,
        motivo: str = None,
        updated_by=None
    ) -> Funcionario:
        """Coloca funcionario como afastado."""
        funcionario.status = Funcionario.Status.AFASTADO
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def registrar_ferias(funcionario: Funcionario, updated_by=None) -> Funcionario:
        """Coloca funcionario em ferias."""
        funcionario.status = Funcionario.Status.FERIAS
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def retornar_atividade(funcionario: Funcionario, updated_by=None) -> Funcionario:
        """Retorna funcionario para atividade normal."""
        funcionario.status = Funcionario.Status.ATIVO
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def alterar_cargo(
        funcionario: Funcionario,
        novo_cargo: str,
        novo_salario: Optional[float] = None,
        updated_by=None
    ) -> Funcionario:
        """Altera cargo do funcionario (promocao/mudanca)."""
        funcionario.cargo = novo_cargo
        if novo_salario is not None:
            funcionario.salario = novo_salario
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def transferir_departamento(
        funcionario: Funcionario,
        novo_departamento: str,
        novo_centro_custo: Optional[str] = None,
        updated_by=None
    ) -> Funcionario:
        """Transfere funcionario para outro departamento."""
        funcionario.departamento = novo_departamento
        if novo_centro_custo:
            funcionario.centro_custo = novo_centro_custo
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def alterar_gestor(
        funcionario: Funcionario,
        novo_gestor: Optional[Funcionario],
        updated_by=None
    ) -> Funcionario:
        """Altera o gestor do funcionario."""
        funcionario.gestor = novo_gestor
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    def get_subordinados(funcionario: Funcionario) -> list:
        """Retorna lista de subordinados diretos."""
        return list(Funcionario.objects.filter(
            gestor=funcionario,
            deleted_at__isnull=True
        ).select_related('pessoa_fisica'))

    @staticmethod
    def get_arvore_hierarquica(funcionario: Funcionario, nivel_max: int = 5) -> dict:
        """Retorna arvore hierarquica do funcionario."""
        def build_tree(func, nivel_atual=0):
            if nivel_atual >= nivel_max:
                return None

            subordinados = Funcionario.objects.filter(
                gestor=func,
                deleted_at__isnull=True
            ).select_related('pessoa_fisica')

            return {
                'id': str(func.id),
                'nome': func.nome,
                'cargo': func.cargo,
                'subordinados': [
                    build_tree(sub, nivel_atual + 1)
                    for sub in subordinados
                ]
            }

        return build_tree(funcionario)
