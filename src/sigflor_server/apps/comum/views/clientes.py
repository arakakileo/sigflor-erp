from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Cliente
from ..serializers import (
    ClienteSerializer, 
    ClienteCreateSerializer,
    ClienteListSerializer
)
from ..services import ClienteService
from .. import selectors


class ClienteViewSet(viewsets.ModelViewSet):
    """ViewSet para Cliente."""

    queryset = Cliente.objects.filter(deleted_at__isnull=True)
    serializer_class = ClienteSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ClienteCreateSerializer
        return ClienteSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.cliente_list(search=search, ativo=ativo)

    def retrieve(self, request, pk=None):
        try:
            cliente = selectors.cliente_detail(pk=pk)
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            cliente = Cliente.objects.get(pk=pk, deleted_at__isnull=True)
            ClienteService.delete(cliente, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cliente.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o cliente."""
        try:
            cliente = Cliente.objects.get(pk=pk, deleted_at__isnull=True)
            ClienteService.ativar(
                cliente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa o cliente."""
        try:
            cliente = Cliente.objects.get(pk=pk, deleted_at__isnull=True)
            ClienteService.desativar(
                cliente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {'detail': 'Cliente não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
