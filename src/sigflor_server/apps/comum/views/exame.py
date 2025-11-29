from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.comum.models import Exame
from apps.comum.serializers.exame import ExameSerializer
from apps.comum.permissions import HasPermission


class ExameViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Exames (entidades mestre).
    Permite operações CRUD e inclui filtros, busca e ordenação.
    """
    queryset = Exame.objects.filter(deleted_at__isnull=True)  # Apenas exames ativos
    serializer_class = ExameSerializer
    permission_classes = [] # Será definido pelo get_permissions
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nome', 'created_at']
    search_fields = ['nome']
    ordering_fields = ['nome', 'created_at', 'updated_at']

    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view exige.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [HasPermission('comum_exame_visualizar')]
        else:
            permission_classes = [HasPermission('comum_exame_editar')]
        return [permission() for permission in permission_classes]
