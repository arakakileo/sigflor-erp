import uuid
from django.db import models
from django.db.models import Q
from apps.comum.models.base import SoftDeleteModel
from .enums import UnidadeEPI 

class TipoEPI(SoftDeleteModel):
    """
    Representa a Categoria/Requisito do EPI.
    Ex: 'Luva de Vaqueta', 'Protetor Auricular Plug', 'Botina de Segurança'.
    É isto que o Cargo pede.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    nome = models.CharField(
        max_length=100, 
        unique=True, 
        help_text="Nome genérico da proteção. Ex: Luva de Vaqueta"
    )
    
    unidade = models.CharField(
        max_length=10,
        choices=UnidadeEPI.choices,
        default=UnidadeEPI.UNIDADE,
        help_text="Unidade de medida padrão para controle de estoque deste tipo"
    )

    class Meta:
        verbose_name = "Tipo de EPI"
        verbose_name_plural = "Tipos de EPI"
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EPI(SoftDeleteModel):
    """
    Representa o EPI Físico/Comercial com seu CA específico.
    Ex: 'Luva Vaqueta Marca Zanel - CA 12345'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    tipo = models.ForeignKey(
        'sst.TipoEPI',
        on_delete=models.RESTRICT,
        related_name='epis_cadastrados',
        help_text='Tipo de proteção que este EPI atende'
    )
    
    ca = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="CA",
        help_text="Certificado de Aprovação"
    )
    
    fabricante = models.CharField(max_length=100, blank=True, default='')
    modelo = models.CharField(max_length=100, blank=True, default='')
    
    validade_ca = models.DateField(
        null=True, 
        blank=True,
        help_text="Data de validade do certificado junto ao MTE"
    )

    class Meta:
        verbose_name = "EPI (Catálogo)"
        verbose_name_plural = "EPIs (Catálogo)"
        ordering = ['tipo__nome', 'ca']
        indexes = [
            models.Index(fields=['ca']),
        ]

    def __str__(self):
        return f"{self.tipo.nome} - CA: {self.ca} ({self.fabricante})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CargoEPI(SoftDeleteModel):
    """
    Define que um Cargo precisa de um TIPO de EPI, e não de um CA específico.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    cargo = models.ForeignKey(
        'rh.Cargo',
        on_delete=models.CASCADE,
        related_name='epis_obrigatorios'
    )
    
    tipo_epi = models.ForeignKey(
        'sst.TipoEPI',
        on_delete=models.RESTRICT,
        related_name='cargos_demandantes',
        help_text='Tipo de EPI exigido para este cargo'
    )
    
    periodicidade_troca_dias = models.PositiveIntegerField(
        help_text='A cada quantos dias deve ser trocado (vida útil estimada para este cargo)'
    )
    
    quantidade_padrao = models.PositiveIntegerField(
        default=1,
        help_text='Quantidade a ser entregue por vez'
    )
    
    observacoes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'cargos_epis'
        constraints = [
            models.UniqueConstraint(
                fields=['cargo', 'tipo_epi'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_cargo_tipo_epi'
            ),
        ]

    def __str__(self):
        return f"{self.cargo.nome} necessita de {self.tipo_epi.nome}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
