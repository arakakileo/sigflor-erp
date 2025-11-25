# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Contrato
from ..serializers import ContratoSerializer, ContratoCreateSerializer, ContratoListSerializer
from ..services import ContratoService
from .. import selectors


class ContratoViewSet(viewsets.ModelViewSet):
    """ViewSet para Contrato."""

    queryset = Contrato.objects.filter(deleted_at__isnull=True)
    serializer_class = ContratoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return ContratoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ContratoCreateSerializer
        return ContratoSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')
        vigente = self.request.query_params.get('vigente')
        contratante_id = self.request.query_params.get('contratante_id')
        empresa_id = self.request.query_params.get('empresa_id')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        if vigente is not None:
            vigente = vigente.lower() == 'true'

        return selectors.contrato_list(
            search=search,
            ativo=ativo,
            vigente=vigente,
            contratante_id=contratante_id,
            empresa_id=empresa_id
        )

    def retrieve(self, request, pk=None):
        try:
            contrato = selectors.contrato_detail(pk=pk)
            serializer = self.get_serializer(contrato)
            return Response(serializer.data)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            contrato = Contrato.objects.get(pk=pk, deleted_at__isnull=True)
            ContratoService.delete(contrato, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o contrato."""
        try:
            contrato = Contrato.objects.get(pk=pk, deleted_at__isnull=True)
            ContratoService.ativar(
                contrato,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contrato)
            return Response(serializer.data)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa o contrato."""
        try:
            contrato = Contrato.objects.get(pk=pk, deleted_at__isnull=True)
            ContratoService.desativar(
                contrato,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contrato)
            return Response(serializer.data)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def renovar(self, request, pk=None):
        """Renova o contrato."""
        try:
            contrato = Contrato.objects.get(pk=pk, deleted_at__isnull=True)
            nova_data_fim = request.data.get('data_fim')
            novo_valor = request.data.get('valor')

            if not nova_data_fim:
                return Response(
                    {'detail': 'Data de fim e obrigatoria para renovacao.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ContratoService.renovar(
                contrato,
                nova_data_fim=nova_data_fim,
                novo_valor=novo_valor,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contrato)
            return Response(serializer.data)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def vigentes(self, request):
        """Lista contratos vigentes."""
        contratante_id = request.query_params.get('contratante_id')
        empresa_id = request.query_params.get('empresa_id')
        contratos = selectors.contratos_vigentes(
            contratante_id=contratante_id,
            empresa_id=empresa_id
        )
        serializer = ContratoListSerializer(contratos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de contratos."""
        stats = selectors.estatisticas_contratos()
        return Response(stats)

    @action(detail=True, methods=['get'])
    def subcontratos(self, request, pk=None):
        """Lista subcontratos do contrato."""
        try:
            Contrato.objects.get(pk=pk, deleted_at__isnull=True)
            subcontratos = selectors.subcontratos_por_contrato(contrato_id=pk)
            from ..serializers import SubContratoListSerializer
            serializer = SubContratoListSerializer(subcontratos, many=True)
            return Response(serializer.data)
        except Contrato.DoesNotExist:
            return Response(
                {'detail': 'Contrato nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
