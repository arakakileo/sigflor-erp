from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from ..models import Cargo, CargoDocumento
from ..serializers.cargos import (
    CargoSerializer, 
    CargoListSerializer, 
    CargoCreateSerializer, 
    CargoUpdateSerializer,
    CargoSelecaoSerializer,
    CargoDocumentoListSerializer,
    CargoDocumentoCreateSerializer,
    CargoDocumentoUpdateSerializer
)
from ..serializers.funcionarios import FuncionarioListSerializer
from ..services.cargos import CargoService
from .. import selectors


class CargoViewSet(BaseRBACViewSet):

    permissao_leitura = 'rh_cargos_ler'
    permissao_escrita = 'rh_cargos_escrever'

    permissoes_acoes =  {
        'ativar': 'rh_cargos_escrever',
        'desativar': 'rh_cargos_escrever',
        'restaurar': 'rh_cargos_escrever',
        'funcionarios': 'rh_cargos_ler',
        'ativos': 'rh_cargos_ler',
        'estatisticas': 'rh_cargos_ler',
        'selecao': 'rh_cargos_ler',
        'documentos': 'rh_cargo_documento_visualizar',
        'vincular_documento': 'rh_cargo_documento_editar',
        'desvincular_documento': 'rh_cargo_documento_editar',
        'validar_documentos': 'rh_cargo_documento_visualizar',
    }

    queryset = Cargo.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return CargoListSerializer
        if self.action == 'create':
            return CargoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CargoUpdateSerializer
        if self.action == 'selecao':
            return CargoSelecaoSerializer
        if self.action == 'documentos':
            return CargoDocumentoListSerializer
        if self.action == 'vincular_documento':
            return CargoDocumentoCreateSerializer
        return CargoSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        cbo = self.request.query_params.get('cbo')
        ativo = self.request.query_params.get('ativo')

        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.cargo_list(
            user=self.request.user,
            search=search,
            cbo=cbo,
            ativo=ativo
        )

    def retrieve(self, request, pk=None):
        cargo = selectors.cargo_detail(user=request.user, pk=pk)
        serializer = self.get_serializer(cargo)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cargo = CargoService.create(
            user=request.user,
            **serializer.validated_data
        )
        output_serializer = CargoSerializer(cargo)        
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        cargo = CargoService.update(
            cargo=instance,
            user=request.user,
            **serializer.validated_data
        )

        # Recarregar objeto via selector para garantir que os vínculos (prefetch) estejam atualizados
        cargo = selectors.cargo_detail(user=request.user, pk=cargo.pk)

        output_serializer = CargoSerializer(cargo)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        CargoService.delete(instance, user=self.request.user)

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        cargo = selectors.cargo_get_by_id_irrestrito(user=request.user, pk=pk)

        if not cargo:
            return Response(
                {'detail': 'Cargo não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        CargoService.restore(cargo, user=request.user)
        return Response(self.get_serializer(cargo).data)

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        cargo = self.get_object()
        CargoService.ativar(cargo, updated_by=request.user)
        serializer = self.get_serializer(cargo)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        cargo = self.get_object()
        CargoService.desativar(cargo, updated_by=request.user)
        serializer = self.get_serializer(cargo)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def funcionarios(self, request, pk=None):
        self.get_object() 
        funcionarios = selectors.funcionarios_por_cargo(user=request.user, cargo_id=pk)
        serializer = FuncionarioListSerializer(funcionarios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def selecao(self, request):
        cargos = selectors.cargo_list_selection(user=request.user)
        serializer = self.get_serializer(cargos, many=True)
        return Response(serializer.data)

    # ============================================================================
    # Rotas de Documentos (Unificadas)
    # ============================================================================

    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        """Lista documentos exigidos por um cargo."""
        cargo = self.get_object()
        documentos = CargoService.get_documentos_cargo(cargo)
        serializer = CargoDocumentoListSerializer(documentos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def vincular_documento(self, request, pk=None):
        """Adiciona ou atualiza vínculo de documento."""
        cargo = self.get_object()
        serializer = CargoDocumentoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        doc = CargoService.vincular_documento_cargo(
            cargo=cargo,
            user=request.user,
            **serializer.validated_data
        )
        return Response(CargoDocumentoListSerializer(doc).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def desvincular_documento(self, request, pk=None):
        """Remove vínculo de documento. Espera 'cargo_documento_id' no body."""
        cargo = self.get_object()
        doc_id = request.data.get('cargo_documento_id')
        
        if not doc_id:
             return Response(
                {'detail': 'cargo_documento_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        doc = get_object_or_404(CargoDocumento, pk=doc_id, cargo=cargo, deleted_at__isnull=True)
        CargoService.remover_vinculo_documento_cargo(doc, user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def validar_documentos(self, request):
        """Valida se funcionário possui documentos do cargo. Param: funcionario_id."""
        funcionario_id = request.query_params.get('funcionario_id')

        if not funcionario_id:
            return Response(
                {'detail': 'funcionario_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from ..models import Funcionario
        funcionario = get_object_or_404(Funcionario, pk=funcionario_id, deleted_at__isnull=True)
        resultado = CargoService.validar_documentos_funcionario(funcionario)
        return Response(resultado)