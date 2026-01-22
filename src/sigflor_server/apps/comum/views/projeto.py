from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .base import BaseRBACViewSet
from ..models import Projeto
from ..serializers import (
    ProjetoSerializer, 
    ProjetoListSerializer,
    ProjetoCreateSerializer,
    ProjetoUpdateSerializer,
    ProjetoSelecaoSerializer
)
from ..services import ProjetoService
from .. import selectors

class ProjetoViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'cadastros_projetos_ler'
    permissao_escrita = 'cadastros_projetos_escrever'
    permissoes_acoes = {
        'ativar': 'cadastros_projetos_escrever',
        'restaurar': 'comum_projetos_escrever',
        'desativar': 'cadastros_projetos_escrever',
        'selecao': 'cadastros_projetos_ler',
        'estatisticas': 'cadastros_projetos_ler',
    }

    queryset = Projeto.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjetoListSerializer
        if self.action == 'create':
            return ProjetoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjetoUpdateSerializer
        if self.action == 'selecao':
            return ProjetoSelecaoSerializer
        return ProjetoSerializer

    def get_queryset(self):
        busca = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')
        filial_id = self.request.query_params.get('filial')
        cliente_id = self.request.query_params.get('cliente')
        empresa_id = self.request.query_params.get('empresa')


        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.projeto_list(
            user=self.request.user,
            search=busca,
            ativo=ativo,
            filial_id=filial_id,
            cliente_id=cliente_id,
            empresa_id=empresa_id
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)    
        projeto = ProjetoService.create(
            user=request.user,
            **serializer.validated_data
        )
        output_serializer = ProjetoSerializer(projeto)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        ProjetoService.update(
            user=self.request.user,
            projeto=serializer.instance,
            **serializer.validated_data
        )

    def retrieve(self, request, pk=None):
        projeto = selectors.projeto_detail(user=request.user, pk=pk)
        serializer = self.get_serializer(projeto)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        ProjetoService.delete(
            user=self.request.user,
            projeto=instance
        )

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        projeto = selectors.projeto_get_by_id_irrestrito(pk=pk)
        if not projeto:
            return Response(
                {'detail': 'Projeto não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        ProjetoService.restore(projeto, user=request.user)
        return Response(self.get_serializer(projeto).data)

    @action(detail=True, methods=['post'])
    def planejar(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.planejar(projeto=projeto, user=request.user)
        return Response(self.get_serializer(projeto).data)

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.iniciar(projeto=projeto, user=request.user)
        return Response(self.get_serializer(projeto).data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.cancelar(projeto=projeto, user=request.user)
        return Response(self.get_serializer(projeto).data)
        
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.concluir(projeto=projeto, user=request.user)
        return Response(self.get_serializer(projeto).data)
    
    @action(detail=False, methods=['get'])
    def selecao(self, request):
        projetos = selectors.projeto_list_selection(user=request.user)
        serializer = self.get_serializer(projetos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)