from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.comum.models import Projeto
from apps.comum.serializers.projeto import ProjetoSerializer, ProjetoListSerializer
from apps.comum.permissions import HasPermission


class ProjetoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Projetos (Centros de Custo).
    Permite operações CRUD e inclui filtros, busca e ordenação.
    """
    queryset = Projeto.objects.filter(deleted_at__isnull=True) # Apenas projetos ativos
    permission_classes = [] # Será definido pelo get_permissions
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nome', 'cliente', 'filial', 'empresa', 'created_at']
    search_fields = ['nome', 'cliente__pessoa_juridica__nome_fantasia', 'filial__nome', 'empresa__pessoa_juridica__nome_fantasia']
    ordering_fields = ['nome', 'created_at', 'updated_at']

    def get_permissions(self):
        """
        Instancia e retorna a lista de permissões que esta view exige.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [HasPermission('comum_projeto_visualizar')]
        else:
            permission_classes = [HasPermission('comum_projeto_editar')]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjetoListSerializer
        return ProjetoSerializer

    def perform_create(self, serializer):
        # O campo 'empresa' é preenchido automaticamente pelo save() do modelo Projeto
        serializer.save()

    def perform_update(self, serializer):
        # O campo 'empresa' é preenchido automaticamente pelo save() do modelo Projeto
        serializer.save()
