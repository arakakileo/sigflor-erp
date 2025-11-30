# -*- coding: utf-8 -*-
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError

from ..models import Equipe, EquipeFuncionario
from ..serializers import (
    EquipeSerializer,
    EquipeCreateSerializer,
    EquipeListSerializer,
    EquipeUpdateSerializer,
    EquipeFuncionarioSerializer,
    EquipeFuncionarioCreateSerializer,
    EquipeFuncionarioListSerializer,
    FuncionarioListSerializer,
)
from ..services import EquipeService
from .. import selectors


class EquipeViewSet(viewsets.ModelViewSet):
    """ViewSet para Equipe."""

    queryset = Equipe.objects.filter(deleted_at__isnull=True)
    serializer_class = EquipeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return EquipeListSerializer
        if self.action == 'create':
            return EquipeCreateSerializer
        if self.action in ['update', 'partial_update']:
            return EquipeUpdateSerializer
        return EquipeSerializer

    def get_queryset(self):
        busca = self.request.query_params.get('busca')
        projeto_id = self.request.query_params.get('projeto')
        tipo_equipe = self.request.query_params.get('tipo_equipe')
        apenas_ativas = self.request.query_params.get('apenas_ativas', 'true').lower() == 'true'

        return selectors.equipe_list(
            user=self.request.user,
            busca=busca,
            projeto_id=projeto_id,
            tipo_equipe=tipo_equipe,
            apenas_ativas=apenas_ativas
        )

    def retrieve(self, request, pk=None):
        try:
            equipe = selectors.equipe_detail(user=request.user, pk=pk)
            serializer = self.get_serializer(equipe)
            return Response(serializer.data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            EquipeService.delete(
                equipe,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def membros(self, request, pk=None):
        """Lista membros ativos da equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            membros = EquipeService.get_membros_ativos(equipe)
            serializer = FuncionarioListSerializer(membros, many=True)
            return Response(serializer.data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def adicionar_membro(self, request, pk=None):
        """Adiciona um funcionário à equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            serializer = EquipeFuncionarioCreateSerializer(
                data=request.data,
                context={'request': request, 'equipe': equipe}
            )
            if serializer.is_valid():
                equipe_funcionario = serializer.save()
                return Response(
                    EquipeFuncionarioSerializer(equipe_funcionario).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def remover_membro(self, request, pk=None):
        """Remove um funcionário da equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            funcionario_id = request.data.get('funcionario_id')
            data_saida = request.data.get('data_saida')

            if not funcionario_id:
                return Response(
                    {'detail': 'funcionario_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            from ..models import Funcionario
            funcionario = Funcionario.objects.get(pk=funcionario_id, deleted_at__isnull=True)

            equipe_funcionario = EquipeService.remover_membro(
                equipe=equipe,
                funcionario=funcionario,
                data_saida=data_saida,
                updated_by=request.user if request.user.is_authenticated else None
            )
            return Response(EquipeFuncionarioSerializer(equipe_funcionario).data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def definir_lider(self, request, pk=None):
        """Define o líder da equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            lider_id = request.data.get('lider_id')

            if not lider_id:
                return Response(
                    {'detail': 'lider_id é obrigatório.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            from ..models import Funcionario
            lider = Funcionario.objects.get(pk=lider_id, deleted_at__isnull=True)

            equipe = EquipeService.definir_lider(
                equipe=equipe,
                lider=lider,
                updated_by=request.user if request.user.is_authenticated else None
            )
            return Response(EquipeSerializer(equipe).data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def definir_coordenador(self, request, pk=None):
        """Define o coordenador da equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            coordenador_id = request.data.get('coordenador_id')

            from ..models import Funcionario
            coordenador = None
            if coordenador_id:
                coordenador = Funcionario.objects.get(pk=coordenador_id, deleted_at__isnull=True)

            equipe = EquipeService.definir_coordenador(
                equipe=equipe,
                coordenador=coordenador,
                updated_by=request.user if request.user.is_authenticated else None
            )
            return Response(EquipeSerializer(equipe).data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """Retorna histórico de membros da equipe."""
        try:
            equipe = Equipe.objects.get(pk=pk, deleted_at__isnull=True)
            historico = EquipeService.get_historico_membros(equipe)
            serializer = EquipeFuncionarioListSerializer(historico, many=True)
            return Response(serializer.data)
        except Equipe.DoesNotExist:
            return Response(
                {'detail': 'Equipe nao encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )


class EquipeFuncionarioViewSet(viewsets.ModelViewSet):
    """ViewSet para EquipeFuncionario (alocações em equipes)."""

    queryset = EquipeFuncionario.objects.filter(deleted_at__isnull=True)
    serializer_class = EquipeFuncionarioSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return EquipeFuncionarioListSerializer
        if self.action == 'create':
            return EquipeFuncionarioCreateSerializer
        return EquipeFuncionarioSerializer

    def get_queryset(self):
        equipe_id = self.request.query_params.get('equipe')
        funcionario_id = self.request.query_params.get('funcionario')
        apenas_ativos = self.request.query_params.get('apenas_ativos', 'true').lower() == 'true'

        qs = EquipeFuncionario.objects.filter(deleted_at__isnull=True)

        if equipe_id:
            qs = qs.filter(equipe_id=equipe_id)
        if funcionario_id:
            qs = qs.filter(funcionario_id=funcionario_id)
        if apenas_ativos:
            qs = qs.filter(data_saida__isnull=True)

        return qs.select_related(
            'equipe', 'funcionario', 'funcionario__pessoa_fisica'
        ).order_by('-data_entrada')
