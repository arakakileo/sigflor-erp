from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Empresa
from ..serializers import (
    EmpresaSerializer, 
    EmpresaCreateSerializer, 
    EmpresaListSerializer
)
from ..services import EmpresaService
from .. import selectors


class EmpresaViewSet(viewsets.ModelViewSet):
    """ViewSet para Empresa."""

    queryset = Empresa.objects.filter(deleted_at__isnull=True)
    serializer_class = EmpresaSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EmpresaCreateSerializer
        return EmpresaSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativa = self.request.query_params.get('ativa')

        if ativa is not None:
            ativa = ativa.lower() == 'true'

        return selectors.empresa_list(search=search, ativa=ativa)

    def retrieve(self, request, pk=None):
        try:
            empresa = selectors.empresa_detail(pk=pk)
            serializer = self.get_serializer(empresa)
            return Response(serializer.data)
        except Empresa.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            empresa = Empresa.objects.get(pk=pk, deleted_at__isnull=True)
            EmpresaService.delete(empresa, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Empresa.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def tornar_matriz(self, request, pk=None):
        """Define esta empresa como matriz."""
        try:
            empresa = Empresa.objects.get(pk=pk, deleted_at__isnull=True)
            EmpresaService.tornar_matriz(
                empresa,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(empresa)
            return Response(serializer.data)
        except Empresa.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
