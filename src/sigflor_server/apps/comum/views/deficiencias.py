# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Deficiencia
from ..serializers import (
    DeficienciaSerializer,
    DeficienciaCreateSerializer,
    DeficienciaListSerializer,
    PessoaFisicaSerializer
)
from ..services import DeficienciaService
from .. import selectors


class DeficienciaViewSet(viewsets.ModelViewSet):
    """ViewSet para Deficiencia."""

    queryset = Deficiencia.objects.filter(deleted_at__isnull=True)
    serializer_class = DeficienciaSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return DeficienciaListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return DeficienciaCreateSerializer
        return DeficienciaSerializer

    def get_queryset(self):
        pessoa_fisica_id = self.request.query_params.get('pessoa_fisica_id')
        search = self.request.query_params.get('search')
        tipo = self.request.query_params.get('tipo')
        cid = self.request.query_params.get('cid')

        return selectors.deficiencia_list(
            pessoa_fisica_id=pessoa_fisica_id,
            search=search,
            tipo=tipo,
            cid=cid
        )

    def retrieve(self, request, pk=None):
        try:
            deficiencia = selectors.deficiencia_detail(pk=pk)
            serializer = self.get_serializer(deficiencia)
            return Response(serializer.data)
        except Deficiencia.DoesNotExist:
            return Response(
                {'detail': 'Deficiencia nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            deficiencia = Deficiencia.objects.get(pk=pk, deleted_at__isnull=True)
            DeficienciaService.delete(
                deficiencia,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Deficiencia.DoesNotExist:
            return Response(
                {'detail': 'Deficiencia nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de deficiencias."""
        stats = selectors.estatisticas_deficiencias()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def pessoas_com_deficiencia(self, request):
        """Lista pessoas fisicas que possuem deficiencias."""
        pessoas = selectors.pessoas_com_deficiencia()
        serializer = PessoaFisicaSerializer(pessoas, many=True)
        return Response(serializer.data)
