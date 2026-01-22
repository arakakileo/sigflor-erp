from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.comum.views.base import BaseRBACViewSet
from ..models import Exame
from ..serializers.exame import ExameSerializer, ExameSelecaoSerializer
from ..services import ExameService
from .. import selectors


class ExameViewSet(BaseRBACViewSet):
    
    permissao_leitura = 'sst_exame_ler'
    permissao_escrita = 'sst_exame_escrever'
    
    permissoes_acoes = {
        'selecao': 'sst_exame_ler',
        'restaurar': 'sst_exame_escrever',
    }

    queryset = Exame.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'selecao':
            return ExameSelecaoSerializer
        return ExameSerializer

    def get_queryset(self):
        return selectors.exame_list(
            user=self.request.user,
            search=self.request.query_params.get('search')
        )

    def retrieve(self, request, pk=None):
        exame = selectors.exame_detail(user=request.user, pk=pk)
        serializer = self.get_serializer(exame)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = ExameService.create(
            created_by=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = instance

    def perform_update(self, serializer):
        ExameService.update(
            exame=serializer.instance,
            updated_by=self.request.user,
            **serializer.validated_data
        )

    def perform_destroy(self, instance):
        ExameService.delete(instance, user=self.request.user)

    @action(detail=True, methods=['post'])
    def restaurar(self, request, pk=None):
        exame = selectors.exame_get_by_id_irrestrito(user=request.user, pk=pk)
        
        if not exame:
            return Response(
                {'detail': 'Exame não encontrado.'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        ExameService.restore(exame, user=request.user)
        return Response(self.get_serializer(exame).data)

    @action(detail=False, methods=['get'])
    def selecao(self, request):
        exames = selectors.exame_list_selection(user=request.user)
        serializer = self.get_serializer(exames, many=True)
        return Response(serializer.data)