
import uuid
from datetime import date
from django.db import models
from django.db.models import Q
from apps.comum.models.base import SoftDeleteModel

class EntregaEPI(SoftDeleteModel):
    """
    Registra a entrega de um EPI (físico/CA) para um Funcionário.
    Controla validade e necessidade de troca (baseado no CargoEPI).
    """
    class Meta:
        verbose_name = "Entrega de EPI"
        verbose_name_plural = "Entregas de EPI"
        ordering = ['-data_entrega']
        db_table = 'entregas_epi'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    funcionario = models.ForeignKey(
        'rh.Funcionario',
        on_delete=models.RESTRICT,
        related_name='epis_entregues',
        help_text="Funcionário que recebeu o EPI"
    )

    epi = models.ForeignKey(
        'sst.EPI',
        on_delete=models.RESTRICT,
        related_name='entregas',
        help_text="EPI específico (Marca/CA) entregue"
    )

    data_entrega = models.DateField(default=date.today)
    
    data_validade = models.DateField(
        help_text="Data prevista para troca (Baseada na periodicidade do Cargo)"
    )

    quantidade = models.PositiveIntegerField(default=1)

    devolvido = models.BooleanField(
        default=False,
        help_text="Indica se o EPI foi devolvido/baixado"
    )

    data_devolucao = models.DateField(
        null=True, blank=True,
        help_text="Data efetiva da devolução"
    )

    observacoes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.funcionario.nome} - {self.epi} ({self.data_entrega})"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
