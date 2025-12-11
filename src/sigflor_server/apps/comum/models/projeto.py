# -*- coding: utf-8 -*-
import uuid
from django.db import models
from django.utils import timezone
import random

from .base import SoftDeleteModel
from .enums import StatusProjeto


class Projeto(SoftDeleteModel):
    """
    Representa um Projeto (Centro de Custo/Obra) que une Empresa, Cliente e Filial.
    É uma entidade transversal utilizada por diversos módulos.

    O "Tripé" do projeto:
    - Quem Paga: Cliente
    - Quem Fatura: Empresa (automático, via cliente.empresa_gestora)
    - Onde Executa: Filial
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    numero = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Código único gerado automaticamente"
    )

    descricao = models.TextField(
        help_text="Nome ou objeto do projeto (ex: Manutenção da Fazenda X - Bloco Y)"
    )

    cliente = models.ForeignKey(
        'comum.Cliente',
        on_delete=models.PROTECT,
        related_name="projetos",
        help_text="Cliente para quem o serviço está sendo prestado"
    )

    empresa = models.ForeignKey(
        'comum.Empresa',
        on_delete=models.PROTECT,
        related_name="projetos_gerenciados",
        help_text="Empresa do grupo que fatura (automático)"
    )

    filial = models.ForeignKey(
        'comum.Filial',
        on_delete=models.PROTECT,
        related_name="projetos",
        help_text="Base operacional responsável pela execução"
    )

    data_inicio = models.DateField(
        help_text="Data de início das atividades"
    )

    data_fim = models.DateField(
        blank=True,
        null=True,
        help_text="Data de término prevista"
    )

    status = models.CharField(
        max_length=20,
        choices=StatusProjeto.choices,
        default=StatusProjeto.PLANEJADO,
        help_text="Status atual do projeto"
    )

    class Meta:
        db_table = 'projetos'
        verbose_name = "Projeto"
        verbose_name_plural = "Projetos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['numero']),
            models.Index(fields=['status']),
            models.Index(fields=['cliente']),
            models.Index(fields=['filial']),
            models.Index(fields=['empresa']),
            models.Index(fields=['data_inicio']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['numero'],
                name='unique_numero_projeto'
            ),
        ]

    def save(self, *args, **kwargs):
        """
        Antes de salvar:
        1. Gera o número do projeto automaticamente (se novo)
        2. Preenche a empresa com a empresa_gestora do cliente
        """
        if not self.numero:
            self.numero = self._generate_numero()

        if self.cliente and self.cliente.empresa_gestora:
            self.empresa = self.cliente.empresa_gestora

        self.full_clean()
        super().save(*args, **kwargs)

    def _generate_numero(self) -> str:
        """
        Gera um número único para o projeto.
        Formato: PRJ-YYYYMM-NNNN (ex: PRJ-202511-0001)
        """
        now = timezone.now()
        prefix = f"PRJ-{now.year}{now.month:02d}-"

        # Busca o último número do mês atual
        last_projeto = Projeto.objects.filter(
            numero__startswith=prefix
        ).order_by('-numero').first()

        if last_projeto:
            try:
                last_num = int(last_projeto.numero.split('-')[-1])
                new_num = last_num + 1
            except (ValueError, IndexError):
                new_num = 1
        else:
            new_num = 1

        return f"{prefix}{new_num:04d}"

    def __str__(self):
        return f"{self.numero} - {self.descricao[:50]}"

    @property
    def is_ativo(self) -> bool:
        return self.status == StatusProjeto.EM_EXECUCAO

    @property
    def cliente_nome(self) -> str:
        if self.cliente and self.cliente.pessoa_juridica:
            return self.cliente.pessoa_juridica.nome_fantasia or self.cliente.pessoa_juridica.razao_social
        return ""

    @property
    def empresa_nome(self) -> str:
        if self.empresa and self.empresa.pessoa_juridica:
            return self.empresa.pessoa_juridica.nome_fantasia or self.empresa.pessoa_juridica.razao_social
        return ""

    @property
    def filial_nome(self) -> str:
        return self.filial.nome if self.filial else ""
