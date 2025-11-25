from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Permissao, Papel
from ..serializers import PermissaoSerializer, PapelSerializer
from ..services import PermissaoService
from .. import selectors


class PermissaoViewSet(viewsets.ModelViewSet):
    """ViewSet para Permissao."""

    queryset = Permissao.objects.filter(deleted_at__isnull=True)
    serializer_class = PermissaoSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        return selectors.permissao_list(search=search)

    def destroy(self, request, pk=None):
        try:
            permissao = Permissao.objects.get(pk=pk, deleted_at__isnull=True)
            PermissaoService.delete_permissao(
                permissao,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Permissao.DoesNotExist:
            return Response(
                {'detail': 'Permissão não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )


class PapelViewSet(viewsets.ModelViewSet):
    """ViewSet para Papel."""

    queryset = Papel.objects.filter(deleted_at__isnull=True)
    serializer_class = PapelSerializer

    def get_serializer_class(self):
        return PapelSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        return selectors.papel_list(search=search)

    def retrieve(self, request, pk=None):
        try:
            papel = selectors.papel_detail(pk=pk)
            serializer = self.get_serializer(papel)
            return Response(serializer.data)
        except Papel.DoesNotExist:
            return Response(
                {'detail': 'Papel não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            papel = Papel.objects.get(pk=pk, deleted_at__isnull=True)
            PermissaoService.delete_papel(
                papel,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Papel.DoesNotExist:
            return Response(
                {'detail': 'Papel não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def adicionar_permissao(self, request, pk=None):
        """Adiciona uma permissão ao papel."""
        try:
            papel = Papel.objects.get(pk=pk, deleted_at__isnull=True)
            permissao_id = request.data.get('permissao_id')
            if not permissao_id:
                return Response(
                    {'detail': 'permissao_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            PermissaoService.adicionar_permissao_papel(papel, permissao_id)
            serializer = self.get_serializer(papel)
            return Response(serializer.data)
        except Papel.DoesNotExist:
            return Response(
                {'detail': 'Papel não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remover_permissao(self, request, pk=None):
        """Remove uma permissão do papel."""
        try:
            papel = Papel.objects.get(pk=pk, deleted_at__isnull=True)
            permissao_id = request.data.get('permissao_id')
            if not permissao_id:
                return Response(
                    {'detail': 'permissao_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            PermissaoService.remover_permissao_papel(papel, permissao_id)
            serializer = self.get_serializer(papel)
            return Response(serializer.data)
        except Papel.DoesNotExist:
            return Response(
                {'detail': 'Papel não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
