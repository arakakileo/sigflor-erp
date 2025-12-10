# -*- coding: utf-8 -*-
from typing import Optional
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.comum.models import PessoaFisica
from apps.comum.services import PessoaFisicaService
from ..models import Funcionario, Alocacao, EquipeFuncionario, Equipe
from .cargo_documento import CargoDocumentoService


class FuncionarioService:

    @staticmethod
    @transaction.atomic
    def admitir_funcionario(
        *,
        pessoa_fisica_data: dict,
        funcionario_data: dict,
        created_by=None,
    ) -> Funcionario:
        """
        Realiza a admissão de um novo funcionário.

        Fluxo:
        1. Cria ou recupera a PessoaFisica via PessoaFisicaService
        2. Gera matrícula automática
        3. Valida e define salário nominal
        4. Cria o registro de Funcionário
        5. Cria alocação inicial se projeto informado

        Args:
            pessoa_fisica_data: Dados da pessoa física (incluindo endereços, contatos, documentos)
            funcionario_data: Dados do funcionário (empresa, cargo, projeto, etc.)
            created_by: Usuário que está realizando a operação

        Returns:
            Funcionario: Instância do funcionário criado

        Raises:
            ValidationError: Se dados inválidos ou funcionário já existe
        """
        # 1. Gerenciamento de PessoaFisica
        cpf = pessoa_fisica_data.get('cpf')
        if cpf:
            # Tenta buscar pessoa física existente pelo CPF
            pessoa_fisica = PessoaFisica.objects.filter(
                cpf=cpf.replace('.', '').replace('-', ''),
                deleted_at__isnull=True
            ).first()

            if pessoa_fisica:
                # Verifica se já existe funcionário para esta pessoa
                if Funcionario.objects.filter(
                    pessoa_fisica=pessoa_fisica,
                    deleted_at__isnull=True
                ).exists():
                    raise ValidationError(
                        'Já existe um funcionário cadastrado para esta pessoa física.'
                    )
            else:
                # Cria nova pessoa física
                pessoa_fisica = PessoaFisicaService.create(
                    created_by=created_by,
                    **pessoa_fisica_data
                )
        else:
            # Cria nova pessoa física sem CPF prévio
            pessoa_fisica = PessoaFisicaService.create(
                created_by=created_by,
                **pessoa_fisica_data
            )

        # 2. Validação e Definição do Salário
        cargo = funcionario_data.get('cargo')
        salario_nominal = funcionario_data.get('salario_nominal')

        if cargo:
            if salario_nominal is None:
                # Se não informado, assume o salário base do cargo
                if cargo.salario_base:
                    funcionario_data['salario_nominal'] = cargo.salario_base
                else:
                    raise ValidationError(
                        'Salário nominal é obrigatório quando o cargo não possui salário base definido.'
                    )
            else:
                # Valida que seja >= salário base do cargo
                if cargo.salario_base and Decimal(str(salario_nominal)) < cargo.salario_base:
                    raise ValidationError(
                        f'O salário nominal ({salario_nominal}) não pode ser inferior '
                        f'ao salário base do cargo ({cargo.salario_base}).'
                    )

        # 3. Extrai projeto para alocação posterior
        projeto = funcionario_data.get('projeto')
        data_admissao = funcionario_data.get('data_admissao', timezone.now().date())

        # 4. Criação do Funcionário (matrícula será gerada no save())
        funcionario = Funcionario(
            pessoa_fisica=pessoa_fisica,
            created_by=created_by,
            **funcionario_data
        )
        funcionario.save()

        if funcionario.cargo:
            validacao = CargoDocumentoService.validar_documentos_funcionario(funcionario)

            if not validacao['valido']:
                # Formata a mensagem de erro listando o que falta
                faltantes = [
                    f"{doc['tipo_display']} ({doc.get('condicional') or 'Obrigatório'})"
                    for doc in validacao['documentos_faltantes']
                ]

                raise ValidationError({
                    'documentos': f"Documentos obrigatórios para o cargo '{funcionario.cargo.nome}' estão faltando: {', '.join(faltantes)}"
                })
        # ====================================================================

        # 5. Cria alocação inicial se projeto informado
        if projeto: # Certifique-se que a variável 'projeto' foi definida anteriormente no seu código original
            Alocacao.objects.create(
                funcionario=funcionario,
                projeto=projeto,
                data_inicio=data_admissao,
                observacoes='Alocação inicial na admissão',
                created_by=created_by
            )

        return funcionario

    @staticmethod
    @transaction.atomic
    def update(funcionario: Funcionario, updated_by=None, **kwargs) -> Funcionario:
        """Atualiza um funcionário existente."""
        # Validação de salário se cargo ou salário alterado
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
        """Soft delete de um funcionário."""
        funcionario.delete(user=user)

    @staticmethod
    @transaction.atomic
    def demitir_funcionario(
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

        funcionario.status = Funcionario.Status.DEMITIDO
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
        """Reativa um funcionário demitido."""
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
        """Coloca funcionário como afastado."""
        funcionario.status = Funcionario.Status.AFASTADO
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def registrar_ferias(funcionario: Funcionario, updated_by=None) -> Funcionario:
        """Coloca funcionário em férias."""
        funcionario.status = Funcionario.Status.FERIAS
        funcionario.updated_by = updated_by
        funcionario.save()
        return funcionario

    @staticmethod
    @transaction.atomic
    def retornar_atividade(funcionario: Funcionario, updated_by=None) -> Funcionario:
        """Retorna funcionário para atividade normal."""
        funcionario.status = Funcionario.Status.ATIVO
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
        # Encerra alocação anterior ativa
        alocacao_ativa = Alocacao.objects.filter(
            funcionario=funcionario,
            data_fim__isnull=True,
            deleted_at__isnull=True
        ).first()

        if alocacao_ativa:
            alocacao_ativa.data_fim = data_inicio
            alocacao_ativa.updated_by = created_by
            alocacao_ativa.save()

        # Atualiza projeto no funcionário
        funcionario.projeto = projeto
        funcionario.updated_by = created_by
        funcionario.save()

        # Cria nova alocação
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
