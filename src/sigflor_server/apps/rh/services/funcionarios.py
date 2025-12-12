# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.comum.services import PessoaFisicaService
from ..models import Funcionario, Alocacao, EquipeFuncionario, Equipe, StatusFuncionario


class FuncionarioService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        pessoa_fisica_data: dict,
        funcionario_data: dict,
    ) -> Funcionario:
        
        cpf = pessoa_fisica_data.pop('cpf')
        pessoa_fisica, _ = PessoaFisicaService.get_or_create_by_cpf(
            cpf=cpf,
            created_by=user,
            **pessoa_fisica_data
        )

        cargo = funcionario_data.get('cargo')
        salario_nominal = funcionario_data.get('salario_nominal')

        if cargo:
            if salario_nominal is None:
                if cargo.salario_base:
                    funcionario_data['salario_nominal'] = cargo.salario_base
                else:
                    raise ValidationError(
                        'Salário nominal é obrigatório quando o cargo não possui salário base definido.'
                    )
            else:
                if cargo.salario_base and Decimal(str(salario_nominal)) < cargo.salario_base:
                    raise ValidationError(
                        f'O salário nominal ({salario_nominal}) não pode ser inferior '
                        f'ao salário base do cargo ({cargo.salario_base}).'
                    )
        
        funcionario = Funcionario(
            pessoa_fisica=pessoa_fisica,
            created_by=user,
            **funcionario_data
        )
        funcionario.save()

        if projeto := funcionario_data.get('projeto'):
            Alocacao.objects.create(
                funcionario=funcionario,
                projeto=projeto,
                data_inicio=funcionario_data.get('data_admissao'),
                created_by=user
            )

        return funcionario

    @staticmethod
    @transaction.atomic
    def adicionar_dependente(
        *,
        funcionario: Funcionario,
        dependente_data: dict,
        user: Usuario
    ):

        pessoa_fisica_data = dependente_data.pop('pessoa_fisica')
        
        return DependenteService.create(
            funcionario=funcionario,
            pessoa_fisica_data=pessoa_fisica_data,
            parentesco=dependente_data.get('parentesco'),
            dependencia_irrf=dependente_data.get('dependencia_irrf'),
            created_by=user
        )

    @staticmethod
    @transaction.atomic
    def adicionar_documentos_lote(
        *,
        funcionario: Funcionario,
        documentos: list[dict],
        user: Usuario
    ):
        
        resultados = []
        for doc_data in documentos:
            doc = DocumentoService.criar_documento_funcionario(
                funcionario=funcionario,
                created_by=user,
                **doc_data
            )
            resultados.append(doc)
        return resultados


    @staticmethod
    @transaction.atomic
    def update(funcionario: Funcionario, updated_by=None, **kwargs) -> Funcionario:
        
        novo_cargo = kwargs.get('cargo')
        novo_salario = kwargs.get('salario_nominal')

        cargo_ref = novo_cargo if novo_cargo else funcionario.cargo

        if novo_salario is not None and cargo_ref and cargo_ref.salario_base:
            if Decimal(str(novo_salario)) < cargo_ref.salario_base:
                raise ValidationError(
                    f'O salário nominal ({novo_salario}) não pode ser inferior '
                    f'ao salário base do cargo ({cargo_ref.salario_base}).'
                )

        for attr, value in kwargs.items():
            if hasattr(funcionario, attr):
                setattr(funcionario, attr, value)

        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def delete(funcionario: Funcionario, user=None) -> None:
        funcionario.delete(user=user)

    @staticmethod
    @transaction.atomic
    def demitir(
        *,
        funcionario: Funcionario,
        data_demissao: Optional[timezone.datetime] = None,
        motivo: Optional[str] = None,
        updated_by=None
    ) -> Funcionario:
        """
        Registra a demissão do funcionário.

        Regras:
        - Define data_demissao e status = DEMITIDO
        - Encerra quaisquer alocações em projeto ativas
        - Remove de quaisquer equipes ativas
        - Remove liderança de equipe (se for líder)
        """
        data_demissao_final = data_demissao or timezone.now().date()

        funcionario.status = StatusFuncionario.DEMITIDO
        funcionario.data_demissao = data_demissao_final
        funcionario.projeto = None  # Remove do projeto
        funcionario.updated_by = updated_by
        funcionario.save()

        # 1. Encerra alocações em projetos ativas
        Alocacao.objects.filter(
            funcionario=funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).update(
            data_fim=data_demissao_final,
            updated_by=updated_by
        )

        # 2. Encerra participações em equipes ativas
        EquipeFuncionario.objects.filter(
            funcionario=funcionario,
            data_saida__isnull=True,
            deleted_at__isnull=True
        ).update(
            data_saida=data_demissao_final,
            updated_by=updated_by
        )

        # 3. Remove liderança de equipes (se for líder)
        Equipe.objects.filter(
            lider=funcionario,
            deleted_at__isnull=True
        ).update(
            lider=None,
            updated_by=updated_by
        )

        # 4. Remove coordenação de equipes (se for coordenador)
        Equipe.objects.filter(
            coordenador=funcionario,
            deleted_at__isnull=True
        ).update(
            coordenador=None,
            updated_by=updated_by
        )

        return funcionario

    @staticmethod
    @transaction.atomic
    def reativar(funcionario: Funcionario, updated_by=None) -> Funcionario:
        funcionario.status = StatusFuncionario.ATIVO
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
        funcionario.status = StatusFuncionario.AFASTADO
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def registrar_ferias(funcionario: Funcionario, updated_by=None) -> Funcionario:
        funcionario.status = StatusFuncionario.FERIAS
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def retornar_atividade(funcionario: Funcionario, updated_by=None) -> Funcionario:
        funcionario.status = StatusFuncionario.ATIVO
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def alterar_cargo(
        funcionario: Funcionario,
        novo_cargo,
        novo_salario: Optional[Decimal] = None,
        updated_by=None
    ) -> Funcionario:
        """
        Altera cargo do funcionário (promoção/mudança).

        Se novo_salario não for informado, mantém o salário atual
        (desde que seja >= salário base do novo cargo).
        """
        salario = novo_salario if novo_salario else funcionario.salario_nominal

        if novo_cargo.salario_base and salario < novo_cargo.salario_base:
            raise ValidationError(
                f'O salário ({salario}) é inferior ao salário base '
                f'do novo cargo ({novo_cargo.salario_base}).'
            )

        funcionario.cargo = novo_cargo
        if novo_salario is not None:
            funcionario.salario_nominal = novo_salario
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def alocar_em_projeto(
        *,
        funcionario: Funcionario,
        projeto,
        data_inicio,
        data_fim=None,
        observacoes: str = None,
        created_by=None
    ) -> Alocacao:
        """
        Aloca funcionário em um projeto.

        Regra: Encerra alocação anterior se existir.
        """
        alocacao_ativa = Alocacao.objects.filter(
            funcionario=funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).first()

        if alocacao_ativa:
            alocacao_ativa.data_fim = data_inicio
            alocacao_ativa.updated_by = created_by
            alocacao_ativa.save()

        funcionario.projeto = projeto
        funcionario.updated_by = created_by
        funcionario.save()

        return Alocacao.objects.create(
            funcionario=funcionario,
            projeto=projeto,
            data_inicio=data_inicio,
            data_fim=data_fim,
            observacoes=observacoes,
            created_by=created_by
        )

    @staticmethod
    @transaction.atomic
    def atualizar_flag_dependentes(funcionario: Funcionario) -> None:
        from ..models import Dependente
        tem = Dependente.objects.filter(
            funcionario=funcionario,
            ativo=True,
            deleted_at__isnull=True
        ).exists()

        if funcionario.tem_dependente != tem:
            funcionario.tem_dependente = tem
            funcionario.save(update_fields=['tem_dependente', 'updated_at'])

    @staticmethod
    def get_historico_alocacoes(funcionario: Funcionario) -> list:
        return list(Alocacao.objects.filter(
            funcionario=funcionario,
            deleted_at__isnull=True
        ).select_related('projeto').order_by('-data_inicio'))
