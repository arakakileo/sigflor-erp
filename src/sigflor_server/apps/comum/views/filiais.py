from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .base import BaseRBACViewSet
from ..models import Filial
from ..serializers import (
    FilialSerializer, 
    FilialCreateSerializer, 
    FilialListSerializer,
    FilialUpdateSerializer,
    FilialSelecaoSerializer
)
from ..services import FilialService
from .. import selectors


class FilialViewSet(BaseRBACViewSet):

    permissao_leitura = 'comum_filiais_ler'
    permissao_escrita = 'comum_filiais_escrever'
    permissoes_acoes =  {
        'ativar': 'comum_filiais_escrever',
        'desativar': 'comum_filiais_escrever',
        'suspender': 'comum_filiais_escrever',
        'restaurar': 'comum_filiais_escrever',
        'ativas': 'comum_filiais_ler',
        'estatisticas': 'comum_filiais_ler',
        'selecao': 'comum_filiais_ler',
    }

    queryset = Filial.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return FilialListSerializer
        if self.action == 'create':
            return FilialCreateSerializer
        if self.action in ['update', 'partial_update']:
            return FilialUpdateSerializer
        if self.action == 'selecao':
            return FilialSelecaoSerializer
        return FilialSerializer

    def get_queryset(self):
        termo_busca = self.request.query_params.get('search')
        status_filtro = self.request.query_params.get('status')
        empresa_id = self.request.query_params.get('empresa_id')

        return selectors.filial_list(
            user=self.request.user,
            search=termo_busca,
            status=status_filtro,
            empresa_id=empresa_id
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filial = FilialService.create(
            user=request.user,
            **serializer.validated_data
        )
        output_serializer = FilialSerializer(filial)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        filial_atualizada = FilialService.update(
            filial=instance,
            user=request.user,
            **serializer.validated_data
        )
        output_serializer = FilialSerializer(filial_atualizada)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        filial = selectors.filial_detail(user=request.user,pk=pk)
        serializer = self.get_serializer(filial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        FilialService.delete(instance, user=self.request.user)

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        filial = selectors.filial_get_by_id_irrestrito(pk=pk)
        
        if not filial:
            return Response(
                {'detail': 'Filial não encontrada.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        FilialService.restore(filial, user=request.user)
        serializer = self.get_serializer(filial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        filial = self.get_object()
        FilialService.ativar(
            filial,
            user=request.user
        )
        serializer = self.get_serializer(filial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        filial = self.get_object()
        FilialService.desativar(
            filial,
            user = request.user
        )
        serializer = self.get_serializer(filial)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def suspender(self, request, pk=None):
        filial = self.get_object()
        FilialService.suspender(
            filial,
            user=request.user
        )
        serializer = self.get_serializer(filial)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        stats = selectors.estatisticas_filiais(
            user=request.user
        )
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def selecao(self, request):
        filiais = selectors.filial_list_selection(user=request.user)
        serializer = self.get_serializer(filiais, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
