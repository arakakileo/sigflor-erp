# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.comum.models.base import SoftDeleteModel
from apps.comum.models.enderecos import Endereco


class Funcionario(SoftDeleteModel):
    """
    Cadastro de funcionários da empresa.
    Representa o vínculo empregatício de uma PessoaFisica com uma Empresa.
    """

    class TipoContrato(models.TextChoices):
        CLT = 'CLT', 'CLT'
        PJ = 'PJ', 'Pessoa Jurídica'
        ESTAGIARIO = 'ESTAGIARIO', 'Estagiário'
        TEMPORARIO = 'TEMPORARIO', 'Temporário'
        APRENDIZ = 'APRENDIZ', 'Jovem Aprendiz'

    class Status(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        AFASTADO = 'AFASTADO', 'Afastado'
        FERIAS = 'FERIAS', 'Em Férias'
        DEMITIDO = 'DEMITIDO', 'Demitido'

    class Turno(models.TextChoices):
        DIURNO = 'DIURNO', 'Diurno'
        NOTURNO = 'NOTURNO', 'Noturno'
        INTEGRAL = 'INTEGRAL', 'Integral'
        FLEXIVEL = 'FLEXIVEL', 'Flexível'

    class TipoConta(models.TextChoices):
        CORRENTE = 'CORRENTE', 'Conta Corrente'
        POUPANCA = 'POUPANCA', 'Conta Poupança'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Vínculo com PessoaFisica (dados pessoais)
    pessoa_fisica = models.OneToOneField(
        'comum.PessoaFisica',
        on_delete=models.PROTECT,
        related_name='funcionario',
        help_text='Dados pessoais do funcionário'
    )

    # Vínculo com empresa do grupo
    empresa = models.ForeignKey(
        'comum.Empresa',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        help_text='Empresa empregadora'
    )

    # Dados profissionais
    matricula = models.CharField(
        max_length=20,
        unique=True,
        help_text='Matrícula única do funcionário'
    )
    cargo = models.ForeignKey(
        'rh.Cargo',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        help_text='Cargo do funcionário'
    )

    # Dados contratuais
    data_admissao = models.DateField(help_text='Data de admissão')
    data_demissao = models.DateField(
        blank=True,
        null=True,
        help_text='Data de demissão (se aplicável)'
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.ATIVO
    )
    tipo_contrato = models.CharField(
        max_length=30,
        choices=TipoContrato.choices
    )
    salario_nominal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Salário contratual'
    )
    turno = models.CharField(
        max_length=20,
        choices=Turno.choices,
        blank=True,
        null=True
    )

    # Vínculo com projeto (Centro de Custo)
    projeto = models.ForeignKey(
        'comum.Projeto',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        blank=True,
        null=True,
        help_text='Projeto/Centro de Custo ao qual o funcionário está alocado'
    )

    # Dados físicos
    peso_corporal = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Peso do funcionário em kg'
    )
    altura = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Altura do funcionário em metros'
    )

    # Dados adicionais
    indicacao = models.TextField(
        blank=True,
        null=True,
        help_text='Informações sobre quem indicou o funcionário'
    )
    cidade_atual = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Cidade de localização do funcionário'
    )

    # Gestor direto (autoreferência)
    gestor_imediato = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        help_text='Gestor direto do funcionário'
    )

    # Dependentes
    tem_dependente = models.BooleanField(
        default=False,
        help_text='Indica se o funcionário possui dependentes cadastrados'
    )

    # Dados de Documentação Trabalhista
    ctps_numero = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Número da CTPS'
    )
    ctps_serie = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Série da CTPS'
    )
    ctps_uf = models.CharField(
        max_length=2,
        choices=Endereco.UF.choices,
        blank=True,
        null=True,
        help_text='UF de emissão da CTPS'
    )
    pis_pasep = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Número do PIS/PASEP'
    )

    # Dados Bancários
    banco = models.CharField(max_length=100, blank=True, null=True)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    conta_corrente = models.CharField(max_length=30, blank=True, null=True)
    tipo_conta = models.CharField(
        max_length=20,
        choices=TipoConta.choices,
        blank=True,
        null=True
    )
    chave_pix = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Chave PIX'
    )

    # Dados de Uniforme/EPI
    tamanho_camisa = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho da camisa (P, M, G, GG, etc.)'
    )
    tamanho_calca = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho da calça (38, 40, 42, etc.)'
    )
    tamanho_calcado = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho do calçado (39, 40, 41, etc.)'
    )

    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['pessoa_fisica__nome_completo']
        indexes = [
            models.Index(fields=['status', 'data_admissao']),
            models.Index(fields=['cargo', 'status']),
            models.Index(fields=['empresa', 'status']),
            models.Index(fields=['projeto']),
        ]

    def __str__(self):
        return f'{self.pessoa_fisica.nome_completo} ({self.matricula})'

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = self._gerar_matricula()
        # Se salário não informado, assume o salário base do cargo
        if self.salario_nominal is None and self.cargo and self.cargo.salario_base:
            self.salario_nominal = self.cargo.salario_base
        self.full_clean()
        return super().save(*args, **kwargs)

    def _gerar_matricula(self):
        """Gera matrícula automática baseada no ano e sequencial."""
        ano = timezone.now().year
        ultimo = Funcionario.all_objects.filter(
            matricula__startswith=str(ano)
        ).order_by('-matricula').first()

        if ultimo:
            try:
                seq = int(ultimo.matricula[4:8]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1

        # Formato: AAAANNNND (Ano + Sequencial 4 dígitos + Dígito de controle)
        base = f'{ano}{seq:04d}'
        digito = self._calcular_digito_controle(base)
        return f'{base}{digito}'

    def _calcular_digito_controle(self, base: str) -> int:
        """Calcula o dígito de controle da matrícula."""
        soma = sum(int(d) * (i + 1) for i, d in enumerate(base))
        return soma % 10

    @property
    def nome(self):
        """Retorna o nome completo do funcionário."""
        return self.pessoa_fisica.nome_completo

    @property
    def cpf(self):
        """Retorna o CPF do funcionário."""
        return self.pessoa_fisica.cpf

    @property
    def cpf_formatado(self):
        """Retorna o CPF formatado."""
        return self.pessoa_fisica.cpf_formatado

    @property
    def is_ativo(self):
        """Verifica se o funcionário está ativo."""
        return self.status == self.Status.ATIVO and self.deleted_at is None

    @property
    def cargo_nome(self):
        """Retorna o nome do cargo."""
        return self.cargo.nome if self.cargo else None

    @property
    def empresa_nome(self):
        """Retorna o nome da empresa."""
        return self.empresa.nome_fantasia if self.empresa else None

    @property
    def projeto_nome(self):
        """Retorna a descrição do projeto."""
        return self.projeto.descricao if self.projeto else None
