# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Cargo
from ..serializers import (
    CargoSerializer,
    CargoCreateSerializer,
    CargoListSerializer,
    FuncionarioListSerializer
)
from ..services import CargoService
from .. import selectors


class CargoViewSet(viewsets.ModelViewSet):
    """ViewSet para Cargo."""

    queryset = Cargo.objects.filter(deleted_at__isnull=True)
    serializer_class = CargoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return CargoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CargoCreateSerializer
        return CargoSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        ativo = self.request.query_params.get('ativo')
        cbo = self.request.query_params.get('cbo')

        # Converte string para boolean
        if ativo is not None:
            ativo = ativo.lower() == 'true'

        return selectors.cargo_list(
            search=search,
            ativo=ativo,
            cbo=cbo
        )

    def retrieve(self, request, pk=None):
        try:
            cargo = selectors.cargo_detail(pk=pk)
            serializer = self.get_serializer(cargo)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            cargo = Cargo.objects.get(pk=pk, deleted_at__isnull=True)
            CargoService.delete(
                cargo,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa um cargo."""
        try:
            cargo = Cargo.objects.get(pk=pk, deleted_at__isnull=True)
            CargoService.ativar(
                cargo,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = CargoSerializer(cargo)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa um cargo."""
        try:
            cargo = Cargo.objects.get(pk=pk, deleted_at__isnull=True)
            CargoService.desativar(
                cargo,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = CargoSerializer(cargo)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def funcionarios(self, request, pk=None):
        """Lista funcionarios de um cargo especifico."""
        try:
            Cargo.objects.get(pk=pk, deleted_at__isnull=True)
            funcionarios = selectors.funcionarios_por_cargo(cargo_id=pk)
            serializer = FuncionarioListSerializer(funcionarios, many=True)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def ativos(self, request):
        """Lista apenas cargos ativos."""
        cargos = selectors.cargos_ativos()
        serializer = CargoListSerializer(cargos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de cargos."""
        stats = selectors.estatisticas_cargos()
        return Response(stats)
