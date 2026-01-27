from django.db import transaction
from django.core.exceptions import ValidationError

from apps.sst.models import TipoEPI, EPI, CargoEPI

class EPIService:
    
    @staticmethod
    @transaction.atomic
    def criar_tipo_epi(*, nome: str, unidade: str) -> TipoEPI:
        if TipoEPI.objects.filter(nome__iexact=nome, deleted_at__isnull=True).exists():
            raise ValidationError(f"Já existe um Tipo de EPI com o nome '{nome}'.")
            
        tipo = TipoEPI(nome=nome, unidade=unidade)
        tipo.full_clean()
        tipo.save()
        return tipo

    @staticmethod
    @transaction.atomic
    def criar_epi(*, tipo: TipoEPI, ca: str, fabricante: str = '', modelo: str = '', validade_ca=None) -> EPI:
        if EPI.objects.filter(ca=ca, deleted_at__isnull=True).exists():
            raise ValidationError(f"Já existe um EPI cadastrado com o CA '{ca}'.")
            
        epi = EPI(
            tipo=tipo,
            ca=ca,
            fabricante=fabricante,
            modelo=modelo,
            validade_ca=validade_ca
        )
        epi.full_clean()
        epi.save()
        return epi

    @staticmethod
    @transaction.atomic
    def vincular_epi_cargo(
        *, 
        cargo, 
        tipo_epi: TipoEPI, 
        periodicidade_troca_dias: int,
        quantidade_padrao: int = 1,
        observacoes: str = ''
    ) -> CargoEPI:
        
        # Verifica se já existe vínculo
        if CargoEPI.objects.filter(
            cargo=cargo, 
            tipo_epi=tipo_epi, 
            deleted_at__isnull=True
        ).exists():
            raise ValidationError(f"O cargo '{cargo.nome}' já possui exigência para '{tipo_epi.nome}'.")
            
        vinculo = CargoEPI(
            cargo=cargo,
            tipo_epi=tipo_epi,
            periodicidade_troca_dias=periodicidade_troca_dias,
            quantidade_padrao=quantidade_padrao,
            observacoes=observacoes
        )
        vinculo.full_clean()
        vinculo.save()
        return vinculo
