# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Dependente
from ..serializers import (
    DependenteSerializer,
    DependenteCreateSerializer,
    DependenteListSerializer,
    FuncionarioListSerializer
)
from ..services import DependenteService
from .. import selectors


class DependenteViewSet(viewsets.ModelViewSet):
    """ViewSet para Dependente."""

    queryset = Dependente.objects.filter(deleted_at__isnull=True)
    serializer_class = DependenteSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return DependenteListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return DependenteCreateSerializer
        return DependenteSerializer

    def get_queryset(self):
        funcionario_id = self.request.query_params.get('funcionario_id')
        search = self.request.query_params.get('search')
        parentesco = self.request.query_params.get('parentesco')
        incluso_ir = self.request.query_params.get('incluso_ir')
        incluso_plano_saude = self.request.query_params.get('incluso_plano_saude')

        # Converte strings para boolean
        if incluso_ir is not None:
            incluso_ir = incluso_ir.lower() == 'true'
        if incluso_plano_saude is not None:
            incluso_plano_saude = incluso_plano_saude.lower() == 'true'

        return selectors.dependente_list(
            funcionario_id=funcionario_id,
            search=search,
            parentesco=parentesco,
            incluso_ir=incluso_ir,
            incluso_plano_saude=incluso_plano_saude
        )

    def retrieve(self, request, pk=None):
        try:
            dependente = selectors.dependente_detail(pk=pk)
            serializer = self.get_serializer(dependente)
            return Response(serializer.data)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            dependente = Dependente.objects.get(pk=pk, deleted_at__isnull=True)
            DependenteService.delete(
                dependente,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def incluir_ir(self, request, pk=None):
        """Inclui dependente na declaracao de IR."""
        try:
            dependente = Dependente.objects.get(pk=pk, deleted_at__isnull=True)
            DependenteService.incluir_ir(
                dependente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = DependenteSerializer(dependente)
            return Response(serializer.data)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def excluir_ir(self, request, pk=None):
        """Exclui dependente da declaracao de IR."""
        try:
            dependente = Dependente.objects.get(pk=pk, deleted_at__isnull=True)
            DependenteService.excluir_ir(
                dependente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = DependenteSerializer(dependente)
            return Response(serializer.data)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def incluir_plano_saude(self, request, pk=None):
        """Inclui dependente no plano de saude."""
        try:
            dependente = Dependente.objects.get(pk=pk, deleted_at__isnull=True)
            DependenteService.incluir_plano_saude(
                dependente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = DependenteSerializer(dependente)
            return Response(serializer.data)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def excluir_plano_saude(self, request, pk=None):
        """Exclui dependente do plano de saude."""
        try:
            dependente = Dependente.objects.get(pk=pk, deleted_at__isnull=True)
            DependenteService.excluir_plano_saude(
                dependente,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = DependenteSerializer(dependente)
            return Response(serializer.data)
        except Dependente.DoesNotExist:
            return Response(
                {'detail': 'Dependente nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatisticas de dependentes."""
        stats = selectors.estatisticas_dependentes()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def funcionarios_com_dependentes(self, request):
        """Lista funcionarios que possuem dependentes."""
        funcionarios = selectors.funcionarios_com_dependentes()
        serializer = FuncionarioListSerializer(funcionarios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def funcionarios_sem_dependentes(self, request):
        """Lista funcionarios que nao possuem dependentes."""
        funcionarios = selectors.funcionarios_sem_dependentes()
        serializer = FuncionarioListSerializer(funcionarios, many=True)
        return Response(serializer.data)
