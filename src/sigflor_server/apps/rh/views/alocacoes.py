# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError

from ..models import Alocacao
from ..serializers import (
    AlocacaoSerializer,
    AlocacaoCreateSerializer,
    AlocacaoListSerializer,
    AlocacaoUpdateSerializer,
)
from ..services import AlocacaoService
from .. import selectors


class AlocacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para Alocacao (alocações em projetos)."""

    queryset = Alocacao.objects.filter(deleted_at__isnull=True)
    serializer_class = AlocacaoSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return AlocacaoListSerializer
        if self.action == 'create':
            return AlocacaoCreateSerializer
        if self.action in ['update', 'partial_update']:
            return AlocacaoUpdateSerializer
        return AlocacaoSerializer

    def get_queryset(self):
        funcionario_id = self.request.query_params.get('funcionario')
        projeto_id = self.request.query_params.get('projeto')
        apenas_ativas = self.request.query_params.get('apenas_ativas', 'false').lower() == 'true'

        return selectors.alocacao_list(
            user=self.request.user,
            funcionario_id=funcionario_id,
            projeto_id=projeto_id,
            apenas_ativas=apenas_ativas
        )

    def retrieve(self, request, pk=None):
        try:
            alocacao = selectors.alocacao_detail(user=request.user, pk=pk)
            serializer = self.get_serializer(alocacao)
            return Response(serializer.data)
        except Alocacao.DoesNotExist:
            return Response(
                {'detail': 'Alocacao nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            alocacao = Alocacao.objects.get(pk=pk, deleted_at__isnull=True)
            AlocacaoService.delete(
                alocacao,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Alocacao.DoesNotExist:
            return Response(
                {'detail': 'Alocacao nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def encerrar(self, request, pk=None):
        """Encerra uma alocação ativa."""
        try:
            alocacao = Alocacao.objects.get(pk=pk, deleted_at__isnull=True)
            data_fim = request.data.get('data_fim')

            if not data_fim:
                return Response(
                    {'detail': 'data_fim é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            alocacao = AlocacaoService.encerrar_alocacao(
                alocacao=alocacao,
                data_fim=data_fim,
                updated_by=request.user if request.user.is_authenticated else None
            )
            return Response(AlocacaoSerializer(alocacao).data)
        except Alocacao.DoesNotExist:
            return Response(
                {'detail': 'Alocacao nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def ativas(self, request):
        """Lista apenas alocações ativas (sem data_fim)."""
        alocacoes = selectors.alocacao_list(user=request.user, apenas_ativas=True)
        serializer = AlocacaoListSerializer(alocacoes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_projeto(self, request):
        """Lista alocações agrupadas por projeto."""
        projeto_id = request.query_params.get('projeto_id')
        apenas_ativas = request.query_params.get('apenas_ativas', 'true').lower() == 'true'

        if not projeto_id:
            return Response(
                {'detail': 'projeto_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.comum.models import Projeto
        try:
            projeto = Projeto.objects.get(pk=projeto_id, deleted_at__isnull=True)
            alocacoes = AlocacaoService.get_alocacoes_projeto(
                projeto=projeto,
                apenas_ativas=apenas_ativas
            )
            serializer = AlocacaoListSerializer(alocacoes, many=True)
            return Response(serializer.data)
        except Projeto.DoesNotExist:
            return Response(
                {'detail': 'Projeto nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def historico_funcionario(self, request):
        """Retorna histórico de alocações de um funcionário."""
        funcionario_id = request.query_params.get('funcionario_id')

        if not funcionario_id:
            return Response(
                {'detail': 'funcionario_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from ..models import Funcionario
        try:
            funcionario = Funcionario.objects.get(pk=funcionario_id, deleted_at__isnull=True)
            historico = AlocacaoService.get_historico_funcionario(funcionario)
            serializer = AlocacaoListSerializer(historico, many=True)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
