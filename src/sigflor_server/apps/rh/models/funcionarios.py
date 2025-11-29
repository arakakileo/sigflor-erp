# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils import timezone

from apps.comum.models.base import SoftDeleteModel
from apps.comum.models import Projeto


class Funcionario(SoftDeleteModel):
    """
    Cadastro de funcionarios da empresa.
    Vinculado a PessoaFisica para dados pessoais.
    """

    class TipoContrato(models.TextChoices):
        CLT = 'clt', 'CLT'
        PJ = 'pj', 'Pessoa Juridica'
        ESTAGIARIO = 'estagiario', 'Estagiario'
        TEMPORARIO = 'temporario', 'Temporario'
        TERCEIRIZADO = 'terceirizado', 'Terceirizado'
        APRENDIZ = 'aprendiz', 'Jovem Aprendiz'

    class Status(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        AFASTADO = 'afastado', 'Afastado'
        FERIAS = 'ferias', 'Em Ferias'
        LICENCA = 'licenca', 'Em Licenca'
        DEMITIDO = 'demitido', 'Demitido'
        APOSENTADO = 'aposentado', 'Aposentado'

    class Turno(models.TextChoices):
        DIURNO = 'diurno', 'Diurno'
        NOTURNO = 'noturno', 'Noturno'
        INTEGRAL = 'integral', 'Integral'
        FLEXIVEL = 'flexivel', 'Flexivel'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Vinculo com PessoaFisica (dados pessoais)
    pessoa_fisica = models.OneToOneField(
        'comum.PessoaFisica',
        on_delete=models.PROTECT,
        related_name='funcionario',
        help_text='Dados pessoais do funcionario'
    )

    # Dados profissionais
    matricula = models.CharField(
        max_length=20,
        unique=True,
        help_text='Matricula unica do funcionario'
    )
    cargo = models.ForeignKey(
        'rh.Cargo',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        help_text='Cargo do funcionario'
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Departamento/Setor'
    )
    subcontrato = models.ForeignKey(
        'comum.SubContrato',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        blank=True,
        null=True,
        help_text='SubContrato para alocacao de custos'
    )

    # Vinculo com projeto (Centro de Custo)
    projeto = models.ForeignKey(
        'comum.Projeto',
        on_delete=models.PROTECT,
        related_name='alocacoes_projeto',
        blank=True,
        null=True,
        help_text='Projeto/Centro de Custo ao qual o funcionario esta alocado'
    )

    # Dados contratuais
    tipo_contrato = models.CharField(
        max_length=20,
        choices=TipoContrato.choices,
        default=TipoContrato.CLT
    )
    data_admissao = models.DateField(help_text='Data de admissao')
    data_demissao = models.DateField(
        blank=True,
        null=True,
        help_text='Data de demissao (se aplicavel)'
    )
    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Salario base'
    )

    # Jornada de trabalho
    carga_horaria_semanal = models.PositiveIntegerField(
        default=44,
        help_text='Carga horaria semanal em horas'
    )
    turno = models.CharField(
        max_length=20,
        choices=Turno.choices,
        default=Turno.DIURNO
    )
    horario_entrada = models.TimeField(
        blank=True,
        null=True,
        help_text='Horario padrao de entrada'
    )
    horario_saida = models.TimeField(
        blank=True,
        null=True,
        help_text='Horario padrao de saida'
    )

    # Status e situacao
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATIVO
    )

    # Dependentes
    tem_dependente = models.BooleanField(
        default=False,
        help_text='Indica se o funcionario possui dependentes cadastrados'
    )

    # Vestimenta / Uniforme
    tamanho_camisa = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho da camisa (PP, P, M, G, GG, XG, etc.)'
    )
    tamanho_calca = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho da calca (36, 38, 40, 42, etc.)'
    )
    tamanho_botina = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Tamanho da botina/calcado (38, 39, 40, 41, etc.)'
    )

    # Dados bancarios
    banco = models.CharField(max_length=100, blank=True, null=True)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    conta = models.CharField(max_length=30, blank=True, null=True)
    tipo_conta = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Corrente, Poupanca, etc.'
    )
    pix = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Chave PIX'
    )

    # Dados adicionais
    ctps_numero = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Numero da CTPS'
    )
    ctps_serie = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Serie da CTPS'
    )
    ctps_uf = models.CharField(
        max_length=2,
        blank=True,
        null=True,
        help_text='UF de emissao da CTPS'
    )
    pis = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Numero do PIS/PASEP'
    )

    # Vinculo com empresa do grupo
    empresa = models.ForeignKey(
        'comum.EmpresaCNPJ',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        blank=True,
        null=True,
        help_text='Empresa do grupo onde esta alocado'
    )

    # Gestor direto
    gestor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        help_text='Gestor direto do funcionario'
    )

    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'funcionarios'
        verbose_name = 'Funcionario'
        verbose_name_plural = 'Funcionarios'
        ordering = ['pessoa_fisica__nome_completo']
        indexes = [
            models.Index(fields=['matricula']),
            models.Index(fields=['status']),
            models.Index(fields=['departamento']),
            models.Index(fields=['data_admissao']),
            models.Index(fields=['subcontrato']),
            models.Index(fields=['projeto']),
        ]

    def __str__(self):
        return f'{self.pessoa_fisica.nome_completo} ({self.matricula})'

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = self._gerar_matricula()
        self.full_clean()
        return super().save(*args, **kwargs)

    def _gerar_matricula(self):
        """Gera matricula automatica baseada no ano e sequencial."""
        ano = timezone.now().year
        ultimo = Funcionario.objects.filter(
            matricula__startswith=str(ano)
        ).order_by('-matricula').first()

        if ultimo:
            try:
                seq = int(ultimo.matricula[-4:]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1

        return f'{ano}{seq:04d}'

    @property
    def nome(self):
        """Retorna o nome completo do funcionario."""
        return self.pessoa_fisica.nome_completo

    @property
    def cpf(self):
        """Retorna o CPF do funcionario."""
        return self.pessoa_fisica.cpf

    @property
    def cpf_formatado(self):
        """Retorna o CPF formatado."""
        return self.pessoa_fisica.cpf_formatado

    # @property
    # def tempo_empresa(self):
    #     """Retorna o tempo de empresa em dias."""
    #     data_fim = self.data_demissao or timezone.now().date()
    #     return (data_fim - self.data_admissao).days

    @property
    def is_ativo(self):
        """Verifica se o funcionario esta ativo."""
        return self.status == self.Status.ATIVO and self.deleted_at is None

    @property
    def cargo_nome(self):
        """Retorna o nome do cargo."""
        return self.cargo.nome if self.cargo else None

    @property
    def subcontrato_numero(self):
        """Retorna o numero do subcontrato."""
        return self.subcontrato.numero if self.subcontrato else None

    @property
    def filial_nome(self):
        """Retorna o nome da filial via subcontrato."""
        return self.subcontrato.filial_nome if self.subcontrato else None

    @property
    def contrato_numero(self):
        """Retorna o numero do contrato via subcontrato."""
        return self.subcontrato.contrato_numero if self.subcontrato else None

    @property
    def contratante_nome(self):
        """Retorna o nome do contratante via subcontrato."""
        return self.subcontrato.contratante_nome if self.subcontrato else None
