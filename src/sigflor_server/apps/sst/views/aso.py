from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from apps.sst.models import ASO, ExameRealizado
from apps.sst.serializers import (
    ASOSerializer, 
    ASOCreateSerializer, 
    ASOConclusaoSerializer,
    ExameRealizadoSerializer,
    ExameRealizadoUpdateSerializer
)
from apps.sst.services.aso import ASOService
from apps.sst import selectors


class ASOViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_aso_ler'
    permissao_escrita = 'sst_aso_escrever'
    
    permissoes_acoes = {
        'concluir': 'sst_aso_escrever',
    }

    queryset = ASO.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return ASOCreateSerializer
        if self.action == 'concluir':
            return ASOConclusaoSerializer
        return ASOSerializer

    def get_queryset(self):
        return selectors.aso_list(
            user=self.request.user,
            funcionario_id=self.request.query_params.get('funcionario'),
            status=self.request.query_params.get('status')
        )

    def retrieve(self, request, pk=None):
        aso = selectors.aso_detail(user=request.user, pk=pk)
        serializer = self.get_serializer(aso)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Gera uma solicitação de ASO.
        Input: { 'funcionario': UUID, 'tipo': STR }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        aso = ASOService.gerar_solicitacao(
            funcionario=serializer.validated_data['funcionario'],
            tipo=serializer.validated_data['tipo'],
            created_by=request.user
        )
        return Response(
            ASOSerializer(aso).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """
        Conclui o ASO.
        Input: { 'resultado': 'APTO', ... }
        """
        aso = selectors.aso_detail(user=request.user, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        aso = ASOService.concluir_aso(
            aso=aso,
            updated_by=request.user,
            **serializer.validated_data
        )
        return Response(ASOSerializer(aso).data)


class ExameRealizadoViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_aso_ler'
    permissao_escrita = 'sst_aso_escrever'
    
    queryset = ExameRealizado.objects.filter(deleted_at__isnull=True)
    serializer_class = ExameRealizadoSerializer

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return ExameRealizadoUpdateSerializer
        return ExameRealizadoSerializer

    def update(self, request, *args, **kwargs):
        """
        Registra o resultado do exame.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        exame_realizado = ASOService.registrar_resultado_exame(
            exame_realizado=instance,
            updated_by=request.user,
            **serializer.validated_data
        )
        
        # Retorna o serializer completo de leitura
        return Response(ExameRealizadoSerializer(exame_realizado).data)
