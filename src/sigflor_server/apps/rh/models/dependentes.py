# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.db.models import Q

from apps.comum.models.base import SoftDeleteModel


class Dependente(SoftDeleteModel):
    """
    Cadastro de dependentes dos funcionários.
    Representa uma pessoa física que possui vínculo de dependência com um Funcionário.
    Os dados civis do dependente são armazenados em PessoaFisica.
    """

    class Parentesco(models.TextChoices):
        FILHO = 'FILHO', 'Filho(a)'
        CONJUGE = 'CONJUGE', 'Cônjuge'
        IRMAO = 'IRMAO', 'Irmão(ã)'
        PAIS = 'PAIS', 'Pais'
        OUTROS = 'OUTROS', 'Outros'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Vínculo com funcionário
    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.CASCADE,
        related_name='dependentes',
        help_text='Funcionário responsável pelo dependente'
    )

    # Vínculo com PessoaFisica (dados civis do dependente)
    pessoa_fisica = models.OneToOneField(
        'comum.PessoaFisica',
        on_delete=models.PROTECT,
        related_name='dependente',
        help_text='Dados civis do dependente'
    )

    # Tipo de parentesco
    parentesco = models.CharField(
        max_length=30,
        choices=Parentesco.choices,
        help_text='Grau de parentesco com o funcionário'
    )

    # Para fins de IR
    dependencia_irrf = models.BooleanField(
        default=False,
        help_text='Indica se é dependente para fins de Imposto de Renda'
    )

    # Status
    ativo = models.BooleanField(
        default=True,
        help_text='Indica se o dependente está ativo'
    )

    class Meta:
        db_table = 'dependentes'
        verbose_name = 'Dependente'
        verbose_name_plural = 'Dependentes'
        ordering = ['funcionario', 'pessoa_fisica__nome_completo']
        indexes = [
            models.Index(fields=['funcionario', 'ativo']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['funcionario', 'pessoa_fisica'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_funcionario_pessoa_fisica_dependente'
            ),
        ]

    def __str__(self):
        return f'{self.pessoa_fisica.nome_completo} ({self.get_parentesco_display()}) - {self.funcionario.matricula}'

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        # Atualiza flag tem_dependente do funcionário
        self._atualizar_flag_funcionario()
        return result

    def delete(self, user=None):
        result = super().delete(user=user)
        # Atualiza flag tem_dependente do funcionário
        self._atualizar_flag_funcionario()
        return result

    def _atualizar_flag_funcionario(self):
        """Atualiza o campo tem_dependente do funcionário."""
        from .funcionarios import Funcionario
        tem_dependentes = Dependente.objects.filter(
            funcionario=self.funcionario,
            ativo=True,
            deleted_at__isnull=True
        ).exists()
        Funcionario.objects.filter(pk=self.funcionario_id).update(
            tem_dependente=tem_dependentes
        )

    @property
    def nome_completo(self):
        """Retorna o nome completo do dependente."""
        return self.pessoa_fisica.nome_completo

    @property
    def cpf(self):
        """Retorna o CPF do dependente."""
        return self.pessoa_fisica.cpf

    @property
    def cpf_formatado(self):
        """Retorna o CPF formatado."""
        return self.pessoa_fisica.cpf_formatado

    @property
    def data_nascimento(self):
        """Retorna a data de nascimento do dependente."""
        return self.pessoa_fisica.data_nascimento

    @property
    def idade(self):
        """Calcula a idade do dependente."""
        if not self.pessoa_fisica.data_nascimento:
            return None
        from django.utils import timezone
        hoje = timezone.now().date()
        nascimento = self.pessoa_fisica.data_nascimento
        idade = hoje.year - nascimento.year
        if (hoje.month, hoje.day) < (nascimento.month, nascimento.day):
            idade -= 1
        return idade
