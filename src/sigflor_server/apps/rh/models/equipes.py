from django.db import models
from apps.comum.models.base import SoftDeleteModel, AuditModel
from apps.comum.models import Projeto # Importa o modelo Projeto
from .funcionarios import Funcionario


class Equipe(SoftDeleteModel, AuditModel):
    """
    Representa uma equipe de trabalho, vinculada a um Projeto.
    Pode ter um líder e um coordenador.
    """

    class TipoEquipe(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        MECANIZADA = 'mecanizada', 'Mecanizada'

    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Equipe")
    tipo_equipe = models.CharField(max_length=20, choices=TipoEquipe.choices, verbose_name="Tipo de Equipe")

    # Uma equipe está alocada a um Projeto (Centro de Custo)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.PROTECT,
        related_name="equipes",
        verbose_name="Projeto"
    )

    # Líder da equipe (pode ser nulo)
    lider = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipes_lideradas",
        verbose_name="Líder da Equipe"
    )

    # Coordenador da equipe (pode ser nulo)
    coordenador = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipes_coordenadas",
        verbose_name="Coordenador da Equipe"
    )

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        verbose_name = "Equipe"
        verbose_name_plural = "Equipes"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['projeto']),
            models.Index(fields=['lider']),
            models.Index(fields=['coordenador']),
        ]

    def __str__(self):
        return self.nome


class EquipeFuncionario(SoftDeleteModel, AuditModel):
    """
    Tabela de relacionamento N:M entre Equipe e Funcionario, com datas de entrada e saída.
    """
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.PROTECT,
        related_name="membros",
        verbose_name="Equipe"
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.PROTECT,
        related_name="alocacoes_equipe",
        verbose_name="Funcionário"
    )
    data_entrada = models.DateField(verbose_name="Data de Entrada na Equipe")
    data_saida = models.DateField(null=True, blank=True, verbose_name="Data de Saída da Equipe")

    class Meta:
        verbose_name = "Membro de Equipe"
        verbose_name_plural = "Membros de Equipe"
        unique_together = ('equipe', 'funcionario', 'data_entrada') # Garante que não haja alocações duplicadas para o mesmo dia
        indexes = [
            models.Index(fields=['equipe']),
            models.Index(fields=['funcionario']),
            models.Index(fields=['data_entrada']),
        ]

    def __str__(self):
        return f"{self.funcionario.pessoa_fisica.nome_completo} em {self.equipe.nome}"
