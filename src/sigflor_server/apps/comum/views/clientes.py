from urllib import request
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .base import BaseRBACViewSet
from ..serializers import (
    ClienteSerializer, 
    ClienteCreateSerializer,
    ClienteListSerializer,
    ClienteSelecaoSerializer,
    ClienteUpdateSerializer
)
from ..models import Cliente
from ..services import ClienteService
from .. import selectors


class ClienteViewSet(BaseRBACViewSet):

    permissao_leitura = 'comum_clientes_ler'
    permissao_escrita = 'comum_clientes_escrever'
    permissoes_acoes =  {
        'ativar': 'comum_clientes_escrever',
        'desativar': 'comum_clientes_escrever',
        'selecao': 'comum_clientes_ler',
        'restaurar': 'comum_clientes_escrever',
    }

    queryset = Cliente.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        if self.action == 'create':
            return ClienteCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ClienteUpdateSerializer 
        if self.action == 'selecao':
            return ClienteSelecaoSerializer
            
        return ClienteSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.cliente_list(
            user = self.request.user,
            search=search, 
            ativo=ativo
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dados = serializer.validated_data
        pessoa_juridica = dados.pop('pessoa_juridica')
        empresa_gestora = dados.pop('empresa_gestora')
        
        cliente = ClienteService.create(
            user=request.user,
            pessoa_juridica_data=pessoa_juridica,
            empresa_gestora=empresa_gestora,
            **dados
        )
        output_serializer = ClienteSerializer(cliente)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        cliente_atualizado = ClienteService.update(
            cliente=instance,
            updated_by=request.user,
            **serializer.validated_data
        )
        output_serializer = ClienteSerializer(cliente_atualizado)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        cliente = selectors.cliente_detail(user = request.user, pk=pk)
        serializer = self.get_serializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
            ClienteService.delete(
                instance, 
                user=self.request.user
            )

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        cliente = selectors.cliente_get_by_id_irrestrito(user=request.user, pk=pk)
        if not cliente:
            return Response(
                {'detail': 'Cliente não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        ClienteService.restore(cliente, user=request.user)
        serializer = self.get_serializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        cliente = self.get_object()
        ClienteService.ativar(
            cliente,
            updated_by=request.user
        )
        serializer = self.get_serializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        cliente = self.get_object()
        ClienteService.desativar(
            cliente,
            updated_by=request.user
        )
        serializer = self.get_serializer(cliente)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def selecao(self, request):
        clientes = selectors.cliente_list_selection(user=request.user)
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
