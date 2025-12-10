# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import CargoDocumento, Cargo
from ..serializers import (
    CargoDocumentoSerializer,
    CargoDocumentoCreateSerializer,
    CargoDocumentoListSerializer,
    CargoDocumentoUpdateSerializer,
)
from ..services import CargoDocumentoService
from .. import selectors


class CargoDocumentoViewSet(viewsets.ModelViewSet):
    # permission_classes = [] # Será definido pelo get_permissions
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = []
    # search_fields = []
    # ordering_fields = []

    # def get_permissions(self):
    #     """
    #     Instancia e retorna a lista de permissões que esta view exige.
    #     """
    #     if self.action in ['list', 'retrieve']:
    #         permission_classes = [HasPermission('rh_cargo_documento_visualizar')]
    #     else:
    #         permission_classes = [HasPermission('rh_cargo_documento_editar')]
    #     return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return CargoDocumentoListSerializer
        if self.action == 'create':
            return CargoDocumentoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CargoDocumentoUpdateSerializer
        return CargoDocumentoSerializer

    def get_queryset(self):
        cargo_id = self.request.query_params.get('cargo')
        obrigatorio = self.request.query_params.get('obrigatorio')

        return selectors.cargo_documento_list(
            user=self.request.user,
            cargo_id=cargo_id,
            apenas_obrigatorios=(obrigatorio.lower() == 'true') if obrigatorio else False
        )

    def retrieve(self, request, pk=None):
        try:
            cargo_doc = selectors.cargo_documento_detail(user=request.user, pk=pk)
            serializer = self.get_serializer(cargo_doc)
            return Response(serializer.data)
        except CargoDocumento.DoesNotExist:
            return Response(
                {'detail': 'CargoDocumento nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            cargo_doc = selectors.cargo_documento_detail(user=request.user, pk=pk)
            CargoDocumentoService.delete(
                cargo_documento = cargo_doc, 
                user=request.user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CargoDocumento.DoesNotExist:
            return Response(
                {'detail': 'CargoDocumento nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def por_cargo(self, request):
        """Lista documentos exigidos por um cargo específico."""
        cargo_id = request.query_params.get('cargo_id')

        if not cargo_id:
            return Response(
                {'detail': 'cargo_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cargo = Cargo.objects.get(pk=cargo_id, deleted_at__isnull=True)
            documentos = CargoDocumentoService.get_documentos_por_cargo(cargo)
            serializer = CargoDocumentoListSerializer(documentos, many=True)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def obrigatorios_cargo(self, request):
        """Lista apenas documentos obrigatórios de um cargo."""
        cargo_id = request.query_params.get('cargo_id')

        if not cargo_id:
            return Response(
                {'detail': 'cargo_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cargo = Cargo.objects.get(pk=cargo_id, deleted_at__isnull=True)
            documentos = CargoDocumentoService.get_documentos_obrigatorios(cargo)
            serializer = CargoDocumentoListSerializer(documentos, many=True)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def validar_funcionario(self, request):
        """Valida se funcionário possui todos os documentos obrigatórios do cargo."""
        funcionario_id = request.query_params.get('funcionario_id')

        if not funcionario_id:
            return Response(
                {'detail': 'funcionario_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from ..models import Funcionario
        try:
            funcionario = Funcionario.objects.get(pk=funcionario_id, deleted_at__isnull=True)
            resultado = CargoDocumentoService.validar_documentos_funcionario(funcionario)
            return Response(resultado)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
