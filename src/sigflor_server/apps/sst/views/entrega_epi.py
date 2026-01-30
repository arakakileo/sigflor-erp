from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from apps.sst.models import EntregaEPI
from apps.sst.serializers import (
    EntregaEPIReadSerializer,
    EntregaEPICreateSerializer
)
from apps.sst.services import EntregaEPIService

class EntregaEPIViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_epi_ler'
    permissao_escrita = 'sst_epi_escrever'
    
    queryset = EntregaEPI.objects.filter(deleted_at__isnull=True)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EntregaEPICreateSerializer
        return EntregaEPIReadSerializer

    def create(self, request, *args, **kwargs):
        """
        Registra a entrega de um EPI.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        entrega = EntregaEPIService.registrar_entrega(
            user=request.user,
            funcionario_id=serializer.validated_data['funcionario'].id,
            epi_id=serializer.validated_data['epi'].id,
            quantidade=serializer.validated_data.get('quantidade', 1),
            data_entrega=serializer.validated_data.get('data_entrega'),
            observacoes=serializer.validated_data.get('observacoes', '')
        )
        
        return Response(
            EntregaEPIReadSerializer(entrega).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        """
        Registra a devolução de um EPI.
        """
        # TODO: Adicionar campos no body se necessário (data_devolucao)
        # Por enquanto pega do body ou assume hoje
        data_devolucao = request.data.get('data_devolucao')
        
        entrega = EntregaEPIService.registrar_devolucao(
            user=request.user,
            entrega_id=pk,
            data_devolucao=data_devolucao
        )
        
        return Response(EntregaEPIReadSerializer(entrega).data)
