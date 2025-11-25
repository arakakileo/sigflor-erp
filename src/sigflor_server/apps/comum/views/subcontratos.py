# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import SubContrato, Filial
from ..serializers import SubContratoSerializer, SubContratoCreateSerializer, SubContratoListSerializer
from ..services import SubContratoService
from .. import selectors


class SubContratoViewSet(viewsets.ModelViewSet):
    """ViewSet para SubContrato."""

    queryset = SubContrato.objects.filter(deleted_at__isnull=True)
    serializer_class = SubContratoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return SubContratoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return SubContratoCreateSerializer
        return SubContratoSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')
        vigente = self.request.query_params.get('vigente')
        filial_id = self.request.query_params.get('filial_id')
        contrato_id = self.request.query_params.get('contrato_id')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        if vigente is not None:
            vigente = vigente.lower() == 'true'

        return selectors.subcontrato_list(
            search=search,
            ativo=ativo,
            vigente=vigente,
            filial_id=filial_id,
            contrato_id=contrato_id
        )

    def retrieve(self, request, pk=None):
        try:
            subcontrato = selectors.subcontrato_detail(pk=pk)
            serializer = self.get_serializer(subcontrato)
            return Response(serializer.data)
        except SubContrato.DoesNotExist:
            return Response(
                {'detail': 'SubContrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            subcontrato = SubContrato.objects.get(pk=pk, deleted_at__isnull=True)
            SubContratoService.delete(subcontrato, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SubContrato.DoesNotExist:
            return Response(
                {'detail': 'SubContrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o subcontrato."""
        try:
            subcontrato = SubContrato.objects.get(pk=pk, deleted_at__isnull=True)
            SubContratoService.ativar(
                subcontrato,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(subcontrato)
            return Response(serializer.data)
        except SubContrato.DoesNotExist:
            return Response(
                {'detail': 'SubContrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa o subcontrato."""
        try:
            subcontrato = SubContrato.objects.get(pk=pk, deleted_at__isnull=True)
            SubContratoService.desativar(
                subcontrato,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(subcontrato)
            return Response(serializer.data)
        except SubContrato.DoesNotExist:
            return Response(
                {'detail': 'SubContrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def transferir_filial(self, request, pk=None):
        """Transfere o subcontrato para outra filial."""
        try:
            subcontrato = SubContrato.objects.get(pk=pk, deleted_at__isnull=True)
            nova_filial_id = request.data.get('filial_id')

            if not nova_filial_id:
                return Response(
                    {'detail': 'ID da nova filial e obrigatorio.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                nova_filial = Filial.objects.get(pk=nova_filial_id, deleted_at__isnull=True)
            except Filial.DoesNotExist:
                return Response(
                    {'detail': 'Filial de destino nao encontrada.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            SubContratoService.transferir_filial(
                subcontrato,
                nova_filial=nova_filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(subcontrato)
            return Response(serializer.data)
        except SubContrato.DoesNotExist:
            return Response(
                {'detail': 'SubContrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def vigentes(self, request):
        """Lista subcontratos vigentes."""
        filial_id = request.query_params.get('filial_id')
        contrato_id = request.query_params.get('contrato_id')
        subcontratos = selectors.subcontratos_vigentes(
            filial_id=filial_id,
            contrato_id=contrato_id
        )
        serializer = SubContratoListSerializer(subcontratos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de subcontratos."""
        stats = selectors.estatisticas_subcontratos()
        return Response(stats)
