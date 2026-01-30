from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.sst.models import EntregaEPI, CargoEPI

class EntregaEPIService:

    @staticmethod
    @transaction.atomic
    def registrar_entrega(
        *,
        user: Usuario,
        funcionario_id,
        epi_id,
        quantidade: int = 1,
        data_entrega = None,
        observacoes: str = ''
    ) -> EntregaEPI:
        """
        Registra a entrega de um EPI.
        Calcula a data de validade baseada na periodicidade definida no Cargo do funcionário.
        """
        from apps.rh.models import Funcionario
        from apps.sst.models import EPI

        funcionario = Funcionario.objects.get(id=funcionario_id)
        epi = EPI.objects.select_related('tipo').get(id=epi_id)

        if not data_entrega:
            data_entrega = date.today()

        # 1. Busca regra do Cargo para calcular validade
        cargo = funcionario.cargo
        data_validade = None
        
        if cargo:
            cargo_epi = CargoEPI.objects.filter(
                cargo=cargo,
                tipo_epi=epi.tipo,
                deleted_at__isnull=True
            ).first()

            if cargo_epi:
                data_validade = data_entrega + relativedelta(days=cargo_epi.periodicidade_troca_dias)
        
        if not data_validade:
             # Se não houver regra, define validade para 1 ano por padrão ou levanta aviso?
             # Por enquanto, assumimos regra obrigatória ou validade manual.
             # Vamos definir validade do CA se houver, ou padrão 365 dias.
             if epi.validade_ca:
                 data_validade = epi.validade_ca
             else:
                 data_validade = data_entrega + relativedelta(days=365)

        entrega = EntregaEPI(
            funcionario=funcionario,
            epi=epi,
            data_entrega=data_entrega,
            data_validade=data_validade,
            quantidade=quantidade,
            observacoes=observacoes,
            created_by=user,
            updated_by=user
        )
        entrega.save()

        return entrega

    @staticmethod
    @transaction.atomic
    def registrar_devolucao(
        *,
        user: Usuario,
        entrega_id,
        data_devolucao = None
    ) -> EntregaEPI:
        
        entrega = EntregaEPI.objects.get(id=entrega_id)
        
        if entrega.devolvido:
             raise ValidationError("EPI já consta como devolvido.")

        if not data_devolucao:
            data_devolucao = date.today()
            
        entrega.devolvido = True
        entrega.data_devolucao = data_devolucao
        entrega.updated_by = user
        entrega.save()
        
        return entrega
