# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Filial
from ..serializers import FilialSerializer, FilialCreateSerializer, FilialListSerializer
from ..services import FilialService
from .. import selectors


class FilialViewSet(viewsets.ModelViewSet):
    """ViewSet para Filial."""

    queryset = Filial.objects.filter(deleted_at__isnull=True)
    serializer_class = FilialSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return FilialListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return FilialCreateSerializer
        return FilialSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        status_param = self.request.query_params.get('status')
        empresa_id = self.request.query_params.get('empresa_id')

        return selectors.filial_list(
            search=search,
            status=status_param,
            empresa_id=empresa_id
        )

    def retrieve(self, request, pk=None):
        try:
            filial = selectors.filial_detail(pk=pk)
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.delete(filial, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.ativar(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.desativar(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def suspender(self, request, pk=None):
        """Suspende a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.suspender(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def ativas(self, request):
        """Lista filiais ativas."""
        empresa_id = request.query_params.get('empresa_id')
        filiais = selectors.filiais_ativas(empresa_id=empresa_id)
        serializer = FilialListSerializer(filiais, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de filiais."""
        stats = selectors.estatisticas_filiais()
        return Response(stats)

    @action(detail=True, methods=['get'])
    def subcontratos(self, request, pk=None):
        """Lista subcontratos da filial."""
        try:
            Filial.objects.get(pk=pk, deleted_at__isnull=True)
            subcontratos = selectors.subcontratos_por_filial(filial_id=pk)
            from ..serializers import SubContratoListSerializer
            serializer = SubContratoListSerializer(subcontratos, many=True)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
