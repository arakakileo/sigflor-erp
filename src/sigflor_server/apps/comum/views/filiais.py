# -*- coding: utf-8 -*-
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import Filial
from ..serializers import FilialSerializer, FilialCreateSerializer, FilialListSerializer
from ..services import FilialService
from .. import selectors


class FilialViewSet(viewsets.ModelViewSet):
    """ViewSet para Filial."""

    queryset = Filial.objects.filter(deleted_at__isnull=True)
    serializer_class = FilialSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return FilialListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return FilialCreateSerializer
        return FilialSerializer

    def get_queryset(self):
        search = self.request.query_params.get('search')
        status_param = self.request.query_params.get('status')
        empresa_id = self.request.query_params.get('empresa_id')

        return selectors.filial_list(
            user=self.request.user,
            search=search,
            status=status_param,
            empresa_id=empresa_id
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            filial = FilialService.create(
                validated_data=serializer.validated_data,
                user=request.user
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))
        output_serializer = FilialSerializer(filial)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            filial = selectors.filial_detail(user=request.user,pk=pk)
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.delete(filial, user=request.user if request.user.is_authenticated else None)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ativar(self, request, pk=None):
        """Ativa a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.ativar(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.desativar(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def suspender(self, request, pk=None):
        """Suspende a filial."""
        try:
            filial = Filial.objects.get(pk=pk, deleted_at__isnull=True)
            FilialService.suspender(
                filial,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(filial)
            return Response(serializer.data)
        except Filial.DoesNotExist:
            return Response(
                {'detail': 'Filial nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def ativas(self, request):
        """Lista filiais ativas."""
        empresa_id = request.query_params.get('empresa_id')
        filiais = selectors.filiais_ativas(empresa_id=empresa_id)
        serializer = FilialListSerializer(filiais, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de filiais."""
        stats = selectors.estatisticas_filiais()
        return Response(stats)
