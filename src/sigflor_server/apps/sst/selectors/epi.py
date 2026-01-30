from django.db.models import QuerySet

from apps.sst.models import TipoEPI, EPI, CargoEPI

class EPISelector:
    
    @staticmethod
    def listar_tipos_epi(user=None) -> QuerySet[TipoEPI]:
        return TipoEPI.objects.filter(deleted_at__isnull=True).order_by('nome')
        
    @staticmethod
    def listar_epis(user=None, *, tipo_id: str = None) -> QuerySet[EPI]:
        qs = EPI.objects.select_related('tipo').filter(
            deleted_at__isnull=True
        ).order_by('tipo__nome', 'ca')
        
        if tipo_id:
            qs = qs.filter(tipo_id=tipo_id)
            
        return qs
        
    @staticmethod
    def listar_epis_por_tipo(user=None, *, tipo_id: str) -> QuerySet[EPI]:
        # Mantendo para compatibilidade se algo usar, mas agora listar_epis faz isso
        return EPISelector.listar_epis(user=user, tipo_id=tipo_id)

    @staticmethod
    def listar_vinculos_cargo_epi(user=None, *, cargo_id: str = None) -> QuerySet[CargoEPI]:
        qs = CargoEPI.objects.select_related('tipo_epi', 'cargo').filter(
            deleted_at__isnull=True
        ).order_by('tipo_epi__nome')
        
        if cargo_id:
            qs = qs.filter(cargo_id=cargo_id)
            
        return qs

    @staticmethod
    def listar_epis_cargo(user=None, *, cargo_id: str) -> QuerySet[CargoEPI]:
        return EPISelector.listar_vinculos_cargo_epi(user=user, cargo_id=cargo_id)
