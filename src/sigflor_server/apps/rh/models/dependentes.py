# -*- coding: utf-8 -*-
import uuid
from django.db import models

from apps.comum.models.base import SoftDeleteModel


class Dependente(SoftDeleteModel):
    """
    Cadastro de dependentes dos funcionarios.
    Armazena dados pessoais do dependente vinculado ao funcionario.
    """

    class Parentesco(models.TextChoices):
        CONJUGE = 'conjuge', 'Conjuge'
        COMPANHEIRO = 'companheiro', 'Companheiro(a)'
        FILHO = 'filho', 'Filho(a)'
        ENTEADO = 'enteado', 'Enteado(a)'
        PAI = 'pai', 'Pai'
        MAE = 'mae', 'Mae'
        IRMAO = 'irmao', 'Irmao(a)'
        AVO = 'avo', 'Avo(o)'
        NETO = 'neto', 'Neto(a)'
        TUTELADO = 'tutelado', 'Menor Tutelado'
        OUTRO = 'outro', 'Outro'

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMININO = 'F', 'Feminino'
        OUTRO = 'O', 'Outro'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Vinculo com funcionario
    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.CASCADE,
        related_name='dependentes',
        help_text='Funcionario responsavel pelo dependente'
    )

    # Dados pessoais do dependente
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        help_text='CPF do dependente (se possuir)'
    )
    data_nascimento = models.DateField(
        blank=True,
        null=True,
        help_text='Data de nascimento'
    )
    sexo = models.CharField(
        max_length=1,
        choices=Sexo.choices,
        blank=True,
        null=True
    )

    # Tipo de parentesco
    parentesco = models.CharField(
        max_length=20,
        choices=Parentesco.choices,
        help_text='Grau de parentesco com o funcionario'
    )

    # Para fins de IR e beneficios
    incluso_ir = models.BooleanField(
        default=False,
        help_text='Indica se e declarado no IR do funcionario'
    )
    incluso_plano_saude = models.BooleanField(
        default=False,
        help_text='Indica se esta incluso no plano de saude'
    )

    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'dependentes'
        verbose_name = 'Dependente'
        verbose_name_plural = 'Dependentes'
        ordering = ['funcionario', 'nome_completo']
        indexes = [
            models.Index(fields=['funcionario']),
            models.Index(fields=['cpf']),
            models.Index(fields=['parentesco']),
        ]

    def __str__(self):
        return f'{self.nome_completo} ({self.get_parentesco_display()}) - {self.funcionario.matricula}'

    def save(self, *args, **kwargs):
        # Limpa CPF
        if self.cpf:
            self.cpf = ''.join(filter(str.isdigit, self.cpf))
        self.full_clean()
        result = super().save(*args, **kwargs)
        # Atualiza flag tem_dependente do funcionario
        self._atualizar_flag_funcionario()
        return result

    def delete(self, user=None):
        result = super().delete(user=user)
        # Atualiza flag tem_dependente do funcionario
        self._atualizar_flag_funcionario()
        return result

    def _atualizar_flag_funcionario(self):
        """Atualiza o campo tem_dependente do funcionario."""
        from .funcionarios import Funcionario
        tem_dependentes = Dependente.objects.filter(
            funcionario=self.funcionario,
            deleted_at__isnull=True
        ).exists()
        Funcionario.objects.filter(pk=self.funcionario_id).update(
            tem_dependente=tem_dependentes
        )

    @property
    def idade(self):
        """Calcula a idade do dependente."""
        if not self.data_nascimento:
            return None
        from django.utils import timezone
        hoje = timezone.now().date()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade

    @property
    def cpf_formatado(self):
        """Retorna CPF formatado."""
        if self.cpf and len(self.cpf) == 11:
            return f"{self.cpf[:3]}.{self.cpf[3:6]}.{self.cpf[6:9]}-{self.cpf[9:]}"
        return self.cpf
