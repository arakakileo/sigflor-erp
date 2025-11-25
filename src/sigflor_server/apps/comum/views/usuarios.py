from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Usuario
from ..serializers import UsuarioSerializer, UsuarioCreateSerializer
from ..services import UsuarioService
from .. import selectors


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para Usuario."""

    queryset = Usuario.objects.filter(deleted_at__isnull=True)
    serializer_class = UsuarioSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.usuario_list(search=search, ativo=ativo)

    def retrieve(self, request, pk=None):
        try:
            usuario = selectors.usuario_detail(pk=pk)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(pk=pk, deleted_at__isnull=True)
            UsuarioService.delete(usuario, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa o usuário."""
        try:
            usuario = Usuario.objects.get(pk=pk, deleted_at__isnull=True)
            UsuarioService.ativar(
                usuario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa o usuário."""
        try:
            usuario = Usuario.objects.get(pk=pk, deleted_at__isnull=True)
            UsuarioService.desativar(
                usuario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def atribuir_papel(self, request, pk=None):
        """Atribui um papel ao usuário."""
        try:
            usuario = Usuario.objects.get(pk=pk, deleted_at__isnull=True)
            papel_id = request.data.get('papel_id')
            if not papel_id:
                return Response(
                    {'detail': 'papel_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            UsuarioService.atribuir_papel(usuario, papel_id)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remover_papel(self, request, pk=None):
        """Remove um papel do usuário."""
        try:
            usuario = Usuario.objects.get(pk=pk, deleted_at__isnull=True)
            papel_id = request.data.get('papel_id')
            if not papel_id:
                return Response(
                    {'detail': 'papel_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            UsuarioService.remover_papel(usuario, papel_id)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def permissoes(self, request, pk=None):
        """Retorna as permissões efetivas do usuário."""
        try:
            usuario = selectors.usuario_detail(pk=pk)
            permissoes = usuario.get_permissoes_efetivas()
            return Response({'permissoes': list(permissoes)})
        except Usuario.DoesNotExist:
            return Response(
                {'detail': 'Usuário não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
