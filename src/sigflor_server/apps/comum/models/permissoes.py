import uuid
from django.db import models

from .base import SoftDeleteModel


class Permissao(SoftDeleteModel):
    """
    Representa o direito de executar uma ação específica no sistema.
    Formato do código: <modulo>.<entidade>.<ação>
    Ex: core.usuarios.criar, core.pessoa_fisica.visualizar
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(
        max_length=100,
        unique=True,
        help_text="Formato: modulo.entidade.acao (ex: core.usuarios.criar)"
    )
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'permissoes'
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.nome} ({self.codigo})'

    def clean(self):
        super().clean()
        if self.codigo:
            self.codigo = self.codigo.strip().lower()


class Papel(SoftDeleteModel):
    """
    Representa um conjunto de permissões atribuídas a uma função/cargo.
    Ex: Administrador, Gerente de Operações, Supervisor de Frota
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)
    permissoes = models.ManyToManyField(
        Permissao,
        blank=True,
        related_name='papeis'
    )

    class Meta:
        db_table = 'papeis'
        verbose_name = 'Papel'
        verbose_name_plural = 'Papéis'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()
        if self.nome:
            self.nome = self.nome.strip()
