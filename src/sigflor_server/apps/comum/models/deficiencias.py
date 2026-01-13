import uuid
from django.db import models
from django.db.models import Q

from .base import SoftDeleteModel
from .enums import TipoDeficiencia, GrauDeficiencia


class Deficiencia(SoftDeleteModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome = models.CharField(
        max_length=200,
        unique=True,
        help_text='Nome/descrição padrão da deficiência'
    )

    tipo = models.CharField(
        max_length=20,
        choices=TipoDeficiencia.choices,
        default=TipoDeficiencia.OUTRA,
        help_text='Classificação do tipo de deficiência'
    )

    cid = models.CharField(
        max_length=10,
        blank=True,
        default='',
        help_text='Código CID (Classificação Internacional de Doenças) padrão'
    )

    descricao = models.TextField(
        blank=True, 
        default='',
        help_text='Descrição técnica ou detalhes adicionais'
    )

    class Meta:
        db_table = 'deficiencias'
        verbose_name = 'Deficiência (Catálogo)'
        verbose_name_plural = 'Deficiências (Catálogo)'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['cid']),
            models.Index(fields=['nome']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['nome'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_deficiencia_nome_ativa'
            ),
            models.UniqueConstraint(
                fields=['cid'],
                condition=Q(deleted_at__isnull=True) & ~Q(cid=''),
                name='uniq_deficiencia_cid_ativa'
            ),
        ]

    def __str__(self):
        cid_str = f' (CID: {self.cid})' if self.cid else ''
        return f'{self.nome}{cid_str}'

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.nome:
            self.nome = self.nome.strip().title()
        if self.cid:
            self.cid = self.cid.strip().upper()
        return super().save(*args, **kwargs)


class PessoaFisicaDeficiencia(SoftDeleteModel):
    """
    Tabela de Vínculo entre Pessoa Física e Deficiência.
    Armazena os detalhes específicos da condição para uma determinada pessoa.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pessoa_fisica = models.ForeignKey(
        'comum.PessoaFisica',
        on_delete=models.CASCADE,
        related_name='deficiencias_vinculadas',
        help_text='Pessoa física portadora'
    )

    deficiencia = models.ForeignKey(
        Deficiencia,
        on_delete=models.PROTECT,
        related_name='vinculos_pessoa_fisica',
        help_text='Deficiência do catálogo'
    )

    grau = models.CharField(
        max_length=50,
        choices=GrauDeficiencia.choices,
        blank=True,
        default='',
        help_text='Grau da deficiência para esta pessoa (leve, moderado, grave, etc.)'
    )

    congenita = models.BooleanField(
        default=False,
        help_text='Indica se a deficiência é congênita (de nascença)'
    )

    observacoes = models.TextField(
        blank=True, 
        default='',
        help_text='Observações específicas sobre o quadro da pessoa'
    )

    class Meta:
        db_table = 'pessoas_fisicas_deficiencias'
        verbose_name = 'Deficiência de Pessoa Física'
        verbose_name_plural = 'Deficiências de Pessoas Físicas'
        ordering = ['pessoa_fisica', 'deficiencia__nome']
        constraints = [
            models.UniqueConstraint(
                fields=['pessoa_fisica', 'deficiencia'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_pf_deficiencia_ativa'
            )
        ]

    def __str__(self):
        return f'{self.pessoa_fisica} - {self.deficiencia.nome}'

    def save(self, *args, **kwargs):
        self.full_clean()
        result = super().save(*args, **kwargs)
        self._atualizar_possui_deficiencia()
        return result

    def delete(self, user=None):
        result = super().delete(user=user)
        self._atualizar_possui_deficiencia()
        return result

    def restore(self, user=None):
        result = super().restore(user=user)
        self._atualizar_possui_deficiencia()
        return result

    def _atualizar_possui_deficiencia(self):

        from .pessoa_fisica import PessoaFisica
        
        tem_deficiencia = PessoaFisicaDeficiencia.objects.filter(
            pessoa_fisica=self.pessoa_fisica,
            deleted_at__isnull=True
        ).exists()
        
        PessoaFisica.objects.filter(pk=self.pessoa_fisica_id).update(
            possui_deficiencia=tem_deficiencia
        )