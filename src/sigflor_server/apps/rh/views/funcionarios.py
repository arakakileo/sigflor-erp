# -*- coding: utf-8 -*-
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.parsers import JSONParser, FormParser


from .utils import NestedMultipartParser
from ..models import Funcionario
from ..serializers import (
    FuncionarioSerializer,
    FuncionarioCreateSerializer,
    FuncionarioListSerializer
)
from ..services import FuncionarioService
from .. import selectors


class FuncionarioViewSet(viewsets.ModelViewSet):

    parser_classes = (JSONParser, NestedMultipartParser, FormParser)

    def get_serializer_class(self):
        if self.action == 'list':
            return FuncionarioListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return FuncionarioCreateSerializer
        return FuncionarioSerializer

    def get_queryset(self):
        busca = self.request.query_params.get('busca')
        status_filter = self.request.query_params.get('status')
        tipo_contrato = self.request.query_params.get('tipo_contrato')
        empresa_id = self.request.query_params.get('empresa_id')
        cargo_id = self.request.query_params.get('cargo_id')
        projeto_id = self.request.query_params.get('projeto_id')
        apenas_ativos = self.request.query_params.get('apenas_ativos', '').lower() == 'true'

        return selectors.funcionario_list(
            user=self.request.user,
            busca=busca,
            status=status_filter,
            tipo_contrato=tipo_contrato,
            empresa_id=empresa_id,
            cargo_id=cargo_id,
            projeto_id=projeto_id,
            apenas_ativos=apenas_ativos
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            funcionario = FuncionarioService.create(
                user=request.user,
                validated_data=serializer.validated_data,
            )
            output_serializer = FuncionarioSerializer(funcionario)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        try:
            funcionario = selectors.funcionario_detail(user=request.user, pk=pk)
            serializer = self.get_serializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            FuncionarioService.delete(
                funcionario,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def demitir(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            data_demissao = request.data.get('data_demissao')
            FuncionarioService.demitir(
                funcionario,
                data_demissao=data_demissao,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def reativar(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            FuncionarioService.reativar(
                funcionario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def afastar(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            motivo = request.data.get('motivo')
            FuncionarioService.afastar(
                funcionario,
                motivo=motivo,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def ferias(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            FuncionarioService.registrar_ferias(
                funcionario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def retornar(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            FuncionarioService.retornar_atividade(
                funcionario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def alterar_cargo(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            novo_cargo = request.data.get('cargo')
            novo_salario = request.data.get('salario')

            if not novo_cargo:
                return Response(
                    {'detail': 'Campo cargo e obrigatorio.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            FuncionarioService.alterar_cargo(
                funcionario,
                novo_cargo=novo_cargo,
                novo_salario=novo_salario,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def transferir(self, request, pk=None):
        try:
            funcionario = Funcionario.objects.get(pk=pk, deleted_at__isnull=True)
            novo_departamento = request.data.get('departamento')
            novo_centro_custo = request.data.get('centro_custo')

            if not novo_departamento:
                return Response(
                    {'detail': 'Campo departamento e obrigatorio.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            FuncionarioService.transferir_departamento(
                funcionario,
                novo_departamento=novo_departamento,
                novo_centro_custo=novo_centro_custo,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = FuncionarioSerializer(funcionario)
            return Response(serializer.data)
        except Funcionario.DoesNotExist:
            return Response(
                {'detail': 'Funcionario nao encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        stats = selectors.estatisticas_rh(user=request.user)
        return Response(stats)

    @action(detail=False, methods=['get'])
    def aniversariantes(self, request):
        mes = request.query_params.get('mes')
        if mes:
            mes = int(mes)
        aniversariantes = selectors.aniversariantes_mes(user=request.user, mes=mes)
        serializer = FuncionarioListSerializer(aniversariantes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ativos(self, request):
        """Lista apenas funcionarios ativos."""
        funcionarios = selectors.funcionarios_ativos(user=request.user)
        serializer = FuncionarioListSerializer(funcionarios, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def afastados(self, request):
        funcionarios = selectors.funcionarios_afastados(user=request.user)
        serializer = FuncionarioListSerializer(funcionarios, many=True)
        return Response(serializer.data)
