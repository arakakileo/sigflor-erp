# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from ..models import Projeto
from ..serializers import (
    ProjetoSerializer, 
    ProjetoListSerializer,
    ProjetoCreateSerializer,
    ProjetoUpdateSerializer
)
from ..services import ProjetoService
from .. import selectors

class ProjetoViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'cadastros_projetos_ler'
    permissao_escrita = 'cadastros_projetos_escrever'
    permissoes_acoes = {
        'ativar': 'cadastros_projetos_escrever',
        'desativar': 'cadastros_projetos_escrever',
        'estatisticas': 'cadastros_projetos_ler',
    }

    # 1. Atributo queryset obrigatório
    queryset = Projeto.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjetoListSerializer
        if self.action == 'create':
            return ProjetoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjetoUpdateSerializer
        return ProjetoSerializer

    def get_queryset(self):
        # Captura filtros da URL
        busca = self.request.query_params.get('busca')
        ativo = self.request.query_params.get('ativo')
        filial_id = self.request.query_params.get('filial')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        # Delega para o Selector (passando user primeiro)
        return selectors.projeto_list(
            user=self.request.user,
            busca=busca,
            ativo=ativo,
            filial_id=filial_id
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nome = serializer.validated_data.pop('nome')
        filial = serializer.validated_data.pop('filial')
        projeto = ProjetoService.create(
            user=request.user,
            nome=nome,
            filial=filial,
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

    def perform_destroy(self, instance):
        ProjetoService.delete(
            user=self.request.user,
            projeto=instance
        )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.ativar(
            user=request.user, 
            projeto=projeto
        )
        return Response(self.get_serializer(projeto).data)

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        projeto = self.get_object()
        ProjetoService.desativar(
            user=request.user, 
            projeto=projeto
        )
        return Response(self.get_serializer(projeto).data)