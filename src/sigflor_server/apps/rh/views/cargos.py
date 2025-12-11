# -*- coding: utf-8 -*-
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError

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
    

    def get_serializer_class(self):
        if self.action == 'list':
            return CargoListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return CargoCreateSerializer
        return CargoSerializer

    def get_queryset(self):
        busca = self.request.query_params.get('busca')
        ativo = self.request.query_params.get('ativo')
        cbo = self.request.query_params.get('cbo')
        nivel = self.request.query_params.get('nivel')
        com_risco = self.request.query_params.get('com_risco')

        # Converte string para boolean
        if ativo is not None:
            ativo = ativo.lower() == 'true'
        if com_risco is not None:
            com_risco = com_risco.lower() == 'true'

        return selectors.cargo_list(
            user=self.request.user,
            busca=busca,
            ativo=ativo,
            cbo=cbo,
            nivel=nivel,
            com_risco=com_risco
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cargo = CargoService.create(
                **serializer.validated_data,
                user=request.user
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))
        output_serializer = CargoSerializer(cargo)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            cargo = selectors.cargo_detail(user=request.user, pk=pk)
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
        try:
            Cargo.objects.get(pk=pk, deleted_at__isnull=True)
            funcionarios = selectors.funcionarios_por_cargo(user=request.user, cargo_id=pk)
            serializer = FuncionarioListSerializer(funcionarios, many=True)
            return Response(serializer.data)
        except Cargo.DoesNotExist:
            return Response(
                {'detail': 'Cargo nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def ativos(self, request):
        cargos = selectors.cargos_ativos(user=request.user)
        serializer = CargoListSerializer(cargos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        stats = selectors.estatisticas_cargos(user=request.user)
        return Response(stats)
