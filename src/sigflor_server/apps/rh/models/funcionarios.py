import uuid
from django.db import models
from django.utils import timezone

from apps.comum.models.base import SoftDeleteModel
from apps.comum.models.enums import UF
from .enums import (
    TipoContrato, 
    StatusFuncionario,
    TipoConta,
    TamanhoCalca,
    TamanhoCamisa,
    TamanhoCalcado,
)


class Funcionario(SoftDeleteModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pessoa_fisica = models.OneToOneField(
        'comum.PessoaFisica',
        on_delete=models.PROTECT,
        related_name='funcionario',
        help_text='Dados pessoais do funcionário'
    )

    empresa = models.ForeignKey(
        'comum.Empresa',
        on_delete=models.PROTECT,
        related_name='funcionarios',
        help_text='Empresa empregadora'
    )

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

    data_admissao = models.DateField(help_text='Data de admissão')

    data_demissao = models.DateField(
        blank=True,
        null=True,
        help_text='Data de demissão (se aplicável)'
    )

    status = models.CharField(
        max_length=30,
        choices=StatusFuncionario.choices,
        default=StatusFuncionario.AGUARDANDO_ADMISSAO
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

    indicacao = models.TextField(
        blank=True, 
        default='',
        help_text='Informações sobre quem indicou o funcionário'
    )

    cidade_atual = models.CharField(
        max_length=100,
        help_text='Cidade de localização do funcionário'
    )

    tem_dependente = models.BooleanField(
        default=False,
        help_text='Indica se o funcionário possui dependentes cadastrados'
    )

    ctps_numero = models.CharField(
        max_length=20,
        help_text='Número da CTPS',
        blank=True,
        null=True
    )
    ctps_serie = models.CharField(
        max_length=10,
        help_text='Série da CTPS',
        blank=True,
        null=True
    )
    ctps_uf = models.CharField(
        max_length=2,
        choices=UF.choices,
        help_text='UF de emissão da CTPS',
        blank=True,
        null=True
    )
    pis_pasep = models.CharField(
        max_length=15,
        help_text='Número do PIS/PASEP',
        blank=True,
        null=True
    )

    banco = models.CharField(max_length=100, blank=True, null=True)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    conta_corrente = models.CharField(max_length=30, blank=True, null=True)
    tipo_conta = models.CharField(
        max_length=20,
        choices=TipoConta.choices,
        blank=True, 
        null=True,
    )
    chave_pix = models.CharField(
        max_length=100,
        blank=True, 
        null=True,
        help_text='Chave PIX'
    )

    tamanho_camisa = models.CharField(
        max_length=10,
        choices=TamanhoCamisa.choices,
        blank=True, 
        default='',
        help_text='Tamanho da camisa (P, M, G, GG, etc.)'
    )

    tamanho_calca = models.CharField(
        max_length=10,
        choices=TamanhoCalca.choices,
        blank=True, 
        default='',
        help_text='Tamanho da calça (38, 40, 42, etc.)'
    )

    tamanho_calcado = models.CharField(
        max_length=10,
        choices=TamanhoCalcado.choices,
        blank=True, 
        default='',
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
        ]

    def __str__(self):
        return f'{self.pessoa_fisica.nome_completo} ({self.matricula})'

    def save(self, *args, **kwargs):
        if not self.matricula:
            self.matricula = self._gerar_matricula()
        if self.salario_nominal is None and self.cargo and self.cargo.salario_base:
            self.salario_nominal = self.cargo.salario_base
        self.full_clean()
        return super().save(*args, **kwargs)

    def _gerar_matricula(self):
        ano = timezone.now().year
        ultimo = Funcionario.objects.filter(
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
        soma = sum(int(d) * (i + 1) for i, d in enumerate(base))
        return soma % 10

    @property
    def nome(self):
        return self.pessoa_fisica.nome_completo

    @property
    def cpf(self):
        return self.pessoa_fisica.cpf

    @property
    def cpf_formatado(self):
        return self.pessoa_fisica.cpf_formatado

    @property
    def is_ativo(self):
        return self.status == StatusFuncionario.ATIVO and self.deleted_at is None

    @property
    def cargo_nome(self):
        return self.cargo.nome if self.cargo else None

    @property
    def empresa_nome(self):
        return self.empresa.nome_fantasia if self.empresa else None

