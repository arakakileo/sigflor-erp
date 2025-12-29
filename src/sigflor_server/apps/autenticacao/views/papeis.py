from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from ..models import Papel
from ..serializers import (
    PapelSerializer, 
    PapelCreateSerializer,
    PapelUpdateSerializer,
    PapelPermissoesBatchSerializer,
    PapelUsuariosListSerializer
)
from ..services import PapelService
from .. import selectors

class PapelViewSet(BaseRBACViewSet):
    

    permissao_leitura = 'autenticacao.view_papel'
    permissao_update = 'autenticacao.change_papel'
    permissao_create = 'autenticacao.add_papel'
    permissao_delete = 'autenticacao.delete_papel'
    
    permissoes_acoes = {
        'usuarios': 'autenticacao.view_papel',
        'adicionar_permissoes': 'autenticacao.change_papel',
        'remover_permissoes': 'autenticacao.change_papel',
    }

    queryset = Papel.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return PapelCreateSerializer
        if self.action in ['update', 'partial_update']:
            return PapelUpdateSerializer
        return PapelSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')

        return selectors.papel_list(
            user=self.request.user,
            search=search
        )

    def perform_create(self, serializer):
        PapelService.create(
            user=self.request.user,
            **serializer.validated_data
        )

    def perform_update(self, serializer):
        PapelService.update(
            user=self.request.user,
            papel=serializer.instance,
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        PapelService.delete(
            user=self.request.user,
            papel=instance
        )

    @action(detail=True, methods=['get'])
    def usuarios(self, request, pk=None):
        papel = self.get_object()
        usuarios = selectors.usuarios_por_papel(user=request.user, papel=papel)
        serializer = PapelUsuariosListSerializer(usuarios, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='adicionar-permissoes')
    def adicionar_permissoes(self, request, pk=None):
        papel = self.get_object()
        serializer = PapelPermissoesBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissoes_objs = serializer.validated_data['permissoes_ids']

        PapelService.adicionar_permissoes(
            user=request.user,
            papel=papel,
            permissoes=permissoes_objs
        )

        return Response(self.get_serializer(papel).data)

    @action(detail=True, methods=['post'], url_path='remover-permissoes')
    def remover_permissoes(self, request, pk=None):
        papel = self.get_object()
        serializer = PapelPermissoesBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permissoes_objs = serializer.validated_data['permissoes_ids']

        PapelService.remover_permissoes(
            user=request.user,
            papel=papel,
            permissoes=permissoes_objs
        )

        return Response(self.get_serializer(papel).data)