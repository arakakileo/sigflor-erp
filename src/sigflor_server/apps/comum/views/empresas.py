from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .base import BaseRBACViewSet
from ..models import Empresa
from ..serializers import (
    EmpresaSerializer, 
    EmpresaCreateSerializer, 
    EmpresaListSerializer,
    EmpresaUpdateSerializer,
    EmpresaSelecaoSerializer
)
from ..services import EmpresaService
from .. import selectors


class EmpresaViewSet(BaseRBACViewSet):

    permissao_leitura = 'comum_empresas_ler'
    permissao_escrita = 'comum_empresas_escrever'
    permissoes_acoes =  {
        'ativar': 'comum_empresas_escrever',
        'desativar': 'comum_empresas_escrever',
        'selecao': 'comum_empresas_ler',
    }

    queryset = Empresa.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaListSerializer
        if self.action == 'create':
            return EmpresaCreateSerializer
        if self.action in ['update', 'partial_update']:
            return EmpresaUpdateSerializer
        if self.action == 'selecao':
            return EmpresaSelecaoSerializer
        return EmpresaSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativa = self.request.query_params.get('ativa')

        if ativa is not None:
            ativa = ativa.lower() == 'true'

        return selectors.empresa_list(search=search, ativa=ativa)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        pessoa_juridica_data = dados.pop('pessoa_juridica')
        empresa = EmpresaService.create(
            user=request.user, 
            pessoa_juridica_data=pessoa_juridica_data,
            **dados
        )
        output_serializer = EmpresaSerializer(empresa)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        pessoa_atualizada = EmpresaService.update(
            empresa=instance,
            updated_by=request.user,
            **serializer.validated_data
        )
        read_serializer = EmpresaSerializer(pessoa_atualizada)
        return Response(read_serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        empresa = selectors.empresa_detail(pk=pk)
        serializer = self.get_serializer(empresa)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        EmpresaService.delete(instance, user=self.request.user)

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        empresa = self.get_object()
        EmpresaService.ativar(empresa, updated_by=request.user)
        serializer = self.get_serializer(empresa)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        empresa = self.get_object()
        EmpresaService.desativar(empresa, updated_by=request.user)
        serializer = self.get_serializer(empresa)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def selecao(self, request):
        empresas = selectors.empresa_list_selection(user=request.user)
        serializer = self.get_serializer(empresas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)