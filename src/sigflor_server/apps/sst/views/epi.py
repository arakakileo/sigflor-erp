from apps.comum.views.base import BaseRBACViewSet

from apps.sst.selectors import EPISelector
from apps.sst.services import EPIService
from apps.sst.serializers import (
    TipoEPISerializer,
    EPISerializer,
    CargoEPISerializer
)
from apps.sst.models import TipoEPI, EPI, CargoEPI

class TipoEPIViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_epi_ler'
    permissao_escrita = 'sst_epi_escrever'
    
    queryset = TipoEPI.objects.filter(deleted_at__isnull=True)
    serializer_class = TipoEPISerializer
    
    def get_queryset(self):
        return EPISelector.listar_tipos_epi()
        
    def perform_create(self, serializer):
        EPIService.criar_tipo_epi(
            nome=serializer.validated_data['nome'],
            unidade=serializer.validated_data['unidade']
        )


class EPIViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_epi_ler'
    permissao_escrita = 'sst_epi_escrever'
    
    queryset = EPI.objects.filter(deleted_at__isnull=True)
    serializer_class = EPISerializer
    
    def get_queryset(self):
        return EPISelector.listar_epis(
            tipo_id=self.request.query_params.get('tipo')
        )
        
    def perform_create(self, serializer):
        EPIService.criar_epi(
            tipo=serializer.validated_data['tipo'],
            ca=serializer.validated_data['ca'],
            fabricante=serializer.validated_data.get('fabricante', ''),
            modelo=serializer.validated_data.get('modelo', ''),
            validade_ca=serializer.validated_data.get('validade_ca')
        )


class CargoEPIViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_epi_ler'
    permissao_escrita = 'sst_epi_escrever'
    
    queryset = CargoEPI.objects.filter(deleted_at__isnull=True)
    serializer_class = CargoEPISerializer
    
    def get_queryset(self):
        return EPISelector.listar_vinculos_cargo_epi(
            cargo_id=self.request.query_params.get('cargo')
        )
        
    def perform_create(self, serializer):
        EPIService.vincular_epi_cargo(
            cargo=serializer.validated_data['cargo'],
            tipo_epi=serializer.validated_data['tipo_epi'],
            periodicidade_troca_dias=serializer.validated_data['periodicidade_troca_dias'],
            quantidade_padrao=serializer.validated_data.get('quantidade_padrao', 1),
            observacoes=serializer.validated_data.get('observacoes', '')
        )
