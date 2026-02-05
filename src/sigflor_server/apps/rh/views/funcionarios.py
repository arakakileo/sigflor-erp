from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
        tem_dependente = self.request.query_params.get('tem_dependente').lower() == 'true'
        
        return selectors.funcionario_list(
            user=self.request.user,
            busca=busca,
            status=status_filter,
            tipo_contrato=tipo_contrato,
            empresa_id=empresa_id,
            cargo_id=cargo_id,
            projeto_id=projeto_id,
            apenas_ativos=apenas_ativos,
            tem_dependente=tem_dependente
        )

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pesoa_fisica_data = serializer.validated_data.pop('pessoa_fisica')
        funcionario_data = serializer.validated_data
        funcionario = FuncionarioService.create(
            user=request.user,
            pessoa_fisica_data=pesoa_fisica_data,
            funcionario_data=funcionario_data
        )
        output_serializer = FuncionarioSerializer(funcionario)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def contratar(self, request, pk=None):
        """
        Efetiva a contratação (Ativação) do funcionário.
        Valida: ASO Admissional, Documentos e EPIs.
        """
        funcionario = self.get_object()
        
        FuncionarioService.contratar(
            funcionario=funcionario,
            user=request.user
        )
        
        serializer = FuncionarioSerializer(funcionario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='dependentes')
    def adicionar_dependente(self, request, pk=None):
        funcionario = self.get_object()
        serializer = DependenteNestedCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dependente = FuncionarioService.adicionar_dependente(
            funcionario=funcionario,
            dependente_data=serializer.validated_data,
            user=request.user
        )
        
        return Response(status=status.HTTP_201_CREATED)

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
                funcionario=funcionario,
                data_demissao=data_demissao,
                updated_by=request.user
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
    
    @action(detail=True, methods=['get'])
    def historico_alocacoes(self, request, pk=None):
        funcionario = self.get_object()
        historico = selectors.get_historico_alocacoes_funcionario(
            user=request.user,
            funcionario=funcionario
        )
        from ..serializers import AlocacaoListSerializer 
        serializer = AlocacaoListSerializer(historico, many=True)
        return Response(serializer.data)
