from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import EmpresaCNPJ
from ..serializers import (
    EmpresaCNPJSerializer, 
    EmpresaCNPJCreateSerializer, 
    EmpresaCNPJListSerializer
)
from ..services import EmpresaCNPJService
from .. import selectors


class EmpresaCNPJViewSet(viewsets.ModelViewSet):
    """ViewSet para EmpresaCNPJ."""

    queryset = EmpresaCNPJ.objects.filter(deleted_at__isnull=True)
    serializer_class = EmpresaCNPJSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaCNPJListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return EmpresaCNPJCreateSerializer
        return EmpresaCNPJSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativa = self.request.query_params.get('ativa')

        if ativa is not None:
            ativa = ativa.lower() == 'true'

        return selectors.empresa_cnpj_list(search=search, ativa=ativa)

    def retrieve(self, request, pk=None):
        try:
            empresa = selectors.empresa_cnpj_detail(pk=pk)
            serializer = self.get_serializer(empresa)
            return Response(serializer.data)
        except EmpresaCNPJ.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            empresa = EmpresaCNPJ.objects.get(pk=pk, deleted_at__isnull=True)
            EmpresaCNPJService.delete(empresa, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except EmpresaCNPJ.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def tornar_matriz(self, request, pk=None):
        """Define esta empresa como matriz."""
        try:
            empresa = EmpresaCNPJ.objects.get(pk=pk, deleted_at__isnull=True)
            EmpresaCNPJService.tornar_matriz(
                empresa,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(empresa)
            return Response(serializer.data)
        except EmpresaCNPJ.DoesNotExist:
            return Response(
                {'detail': 'Empresa não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
