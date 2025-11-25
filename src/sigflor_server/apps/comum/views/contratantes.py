from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Contratante
from ..serializers import ContratanteSerializer, ContratanteCreateSerializer
from ..services import ContratanteService
from .. import selectors


class ContratanteViewSet(viewsets.ModelViewSet):
    """ViewSet para Contratante."""

    queryset = Contratante.objects.filter(deleted_at__isnull=True)
    serializer_class = ContratanteSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ContratanteCreateSerializer
        return ContratanteSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.contratante_list(search=search, ativo=ativo)

    def retrieve(self, request, pk=None):
        try:
            contratante = selectors.contratante_detail(pk=pk)
            serializer = self.get_serializer(contratante)
            return Response(serializer.data)
        except Contratante.DoesNotExist:
            return Response(
                {'detail': 'Contratante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            contratante = Contratante.objects.get(pk=pk, deleted_at__isnull=True)
            ContratanteService.delete(contratante, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contratante.DoesNotExist:
            return Response(
                {'detail': 'Contratante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o contratante."""
        try:
            contratante = Contratante.objects.get(pk=pk, deleted_at__isnull=True)
            ContratanteService.ativar(
                contratante,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contratante)
            return Response(serializer.data)
        except Contratante.DoesNotExist:
            return Response(
                {'detail': 'Contratante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa o contratante."""
        try:
            contratante = Contratante.objects.get(pk=pk, deleted_at__isnull=True)
            ContratanteService.desativar(
                contratante,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contratante)
            return Response(serializer.data)
        except Contratante.DoesNotExist:
            return Response(
                {'detail': 'Contratante não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
