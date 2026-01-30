from apps.comum.views.base import BaseRBACViewSet

from apps.sst.selectors import EPISelector
from apps.sst.services import EPIService
from apps.sst.serializers import (
    TipoEPISerializer,
    EPISerializer,
)
from apps.sst.models import TipoEPI, EPI

class TipoEPIViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_epi_ler'
    permissao_escrita = 'sst_epi_escrever'
    
    queryset = TipoEPI.objects.filter(deleted_at__isnull=True)
    serializer_class = TipoEPISerializer
    
    def get_queryset(self):
        return EPISelector.listar_tipos_epi(user=self.request.user)
        
    def perform_create(self, serializer):
        EPIService.criar_tipo_epi(
            user=self.request.user,
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
            user=self.request.user,
            tipo_id=self.request.query_params.get('tipo')
        )
        
    def perform_create(self, serializer):
        EPIService.criar_epi(
            user=self.request.user,
            tipo=serializer.validated_data['tipo'],
            ca=serializer.validated_data['ca'],
            fabricante=serializer.validated_data.get('fabricante', ''),
            modelo=serializer.validated_data.get('modelo', ''),
            validade_ca=serializer.validated_data.get('validade_ca')
        )

