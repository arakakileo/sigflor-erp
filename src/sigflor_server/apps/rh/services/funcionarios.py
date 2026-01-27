# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.comum.models import Empresa, Projeto
from apps.comum.services import PessoaFisicaService, DocumentoService
from .dependentes import DependenteService
from ..models import (
    Funcionario,
    EquipeFuncionario,
    Equipe,
    StatusFuncionario,
    Cargo
)


class FuncionarioService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        pessoa_fisica_data: dict,
        empresa: Empresa,
        cargo: Cargo,
        tipo_contrato: str,
        data_admissao,
        salario_nominal: Optional[Decimal] = None,
        **dados_cadastrais 
    ) -> Funcionario:
        
        cpf = pessoa_fisica_data.pop('cpf')
        pessoa_fisica, _ = PessoaFisicaService.get_or_create_by_cpf(
            cpf=cpf,
            created_by=user,
            **pessoa_fisica_data
        )

        salario_final = salario_nominal
        if salario_final is None:
            if cargo.salario_base:
                salario_final = cargo.salario_base
            else:
                raise ValidationError(
                    'Salário nominal é obrigatório quando o cargo não possui salário base definido.'
                )
        elif cargo.salario_base and salario_final < cargo.salario_base:
            raise ValidationError(
                'Salário nominal não pode ser inferior ao salário base do cargo.'
            )
        
        funcionario = Funcionario(
            pessoa_fisica=pessoa_fisica,
            empresa=empresa,
            cargo=cargo,
            tipo_contrato=tipo_contrato,
            data_admissao=data_admissao,
            salario_nominal=salario_final,
            created_by=user,
            **dados_cadastrais
        )
        funcionario.save()

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
        """
        Atualiza funcionário e seus dados pessoais.
        """
        
        # 1. Extração de Dados Aninhados (Pessoa Física)
        # Removemos do kwargs para não atrapalhar o setattr do funcionário
        pessoa_fisica_data = kwargs.pop('pessoa_fisica', None)

        # 3. Validações de Negócio (Status/Cargo/Salário)
        novo_status = kwargs.get('status')
        if novo_status == StatusFuncionario.ATIVO:
            # Validação Inter-Módulos (RH -> SST)
            # Verifica se funcionário tem ASO Admissional APTO antes de ativar
            from apps.sst.services.aso import ASOService
            ASOService.validar_pendencias_admissional(funcionario)

        if novo_salario is not None and cargo_ref and cargo_ref.salario_base:
            if Decimal(str(novo_salario)) < cargo_ref.salario_base:
                raise ValidationError(
                    f'O salário nominal ({novo_salario}) não pode ser inferior '
                    f'ao salário base do cargo ({cargo_ref.salario_base}).'
                )

        # 4. Atualização Genérica (Campos do Funcionario)
        for attr, value in kwargs.items():
            if hasattr(funcionario, attr):
                setattr(funcionario, attr, value)

        funcionario.updated_by = updated_by
        funcionario.save()

        # 5. Atualização Delegada (Pessoa Física)
        # Importante: Isso deve vir APÓS o save do funcionário ou ser independente
        if pessoa_fisica_data:
            PessoaFisicaService.update(
                pessoa=funcionario.pessoa_fisica,
                updated_by=updated_by,
                **pessoa_fisica_data
            )
        
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

        funcionario.updated_by = updated_by
        funcionario.save()

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

