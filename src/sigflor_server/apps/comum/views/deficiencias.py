from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .base import BaseRBACViewSet
from ..models import Deficiencia
from ..serializers import (
    DeficienciaSerializer, 
    DeficienciaSelecaoSerializer
)
from ..services import DeficienciaService
from .. import selectors


class DeficienciaViewSet(BaseRBACViewSet): 
    
    permissao_leitura = 'comum_deficiencia_ler'
    permissao_escrita = 'comum_deficiencia_escrever'
    
    permissoes_acoes =  {
        'selecao': 'comum_deficiencia_ler',
        'restaurar': 'comum_deficiencia_escrever',
    }

    queryset = Deficiencia.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'selecao':
            return DeficienciaSelecaoSerializer
        return DeficienciaSerializer

    def get_queryset(self):
        return selectors.deficiencia_list(
            search=self.request.query_params.get('search'),
            tipo=self.request.query_params.get('tipo'),
            cid=self.request.query_params.get('cid')
        )

    def perform_create(self, serializer):
        instance = DeficienciaService.create(
            created_by=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        DeficienciaService.update(
            deficiencia=serializer.instance,
            updated_by=self.request.user,
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        DeficienciaService.delete(instance, user=self.request.user)

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        deficiencia = selectors.deficiencia_get_by_id_irrestrito(pk=pk)
        if not deficiencia:
            return Response(
                {'detail': 'Deficiência não encontrada.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        DeficienciaService.restore(deficiencia, user=request.user)
        return Response(self.get_serializer(deficiencia).data)

    @action(detail=False, methods=['get'])
    def selecao(self, request):
        deficiencias = selectors.deficiencia_list_selection()
        serializer = self.get_serializer(deficiencias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)