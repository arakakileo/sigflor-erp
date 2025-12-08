# -*- coding: utf-8 -*-
import uuid
from django.db import models

from .base import SoftDeleteModel
from .enums import TipoDeficiencia, GrauDeficiencia


class Deficiencia(SoftDeleteModel):
    """
    Cadastro de deficiencias vinculadas a pessoas fisicas.
    Uma pessoa pode ter multiplas deficiencias cadastradas.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='deficiencias',
        help_text='Pessoa fisica portadora da deficiencia'
    )

    nome = models.CharField(
        max_length=200,
        help_text='Nome/descricao da deficiencia'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoDeficiencia.choices,
        default=TipoDeficiencia.OUTRA,
        help_text='Tipo de deficiencia'
    )

    cid = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text='Codigo CID (Classificacao Internacional de Doencas)'
    )

    grau = models.CharField(
        max_length=50,
        choices=GrauDeficiencia.choices,
        blank=True,
        null=True,
        help_text='Grau da deficiencia (leve, moderado, grave, etc.)'
    )

    congenita = models.BooleanField(
        default=False,
        help_text='Indica se a deficiencia e congenita (de nascenca)'
    )

    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'deficiencias'
        verbose_name = 'Deficiencia'
        verbose_name_plural = 'Deficiencias'
        ordering = ['pessoa_fisica', 'nome']
        indexes = [
            models.Index(fields=['pessoa_fisica']),
            models.Index(fields=['cid']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        cid_str = f' (CID: {self.cid})' if self.cid else ''
        return f'{self.nome}{cid_str} - {self.pessoa_fisica.nome_completo}'

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        self._atualizar_flag_pessoa()
        return result

    def delete(self, user=None):
        result = super().delete(user=user)
        self._atualizar_flag_pessoa()
        return result

    def _atualizar_flag_pessoa(self):
        from .pessoa_fisica import PessoaFisica
        tem_deficiencia = Deficiencia.objects.filter(
            pessoa_fisica=self.pessoa_fisica,
            deleted_at__isnull=True
        ).exists()
        PessoaFisica.objects.filter(pk=self.pessoa_fisica_id).update(
            possui_deficiencia=tem_deficiencia
        )
