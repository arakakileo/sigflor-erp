from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Contato
from ..serializers import ContatoSerializer
from ..services import ContatoService


class ContatoViewSet(viewsets.ModelViewSet):
    """ViewSet para Contato."""

    queryset = Contato.objects.filter(deleted_at__isnull=True)
    serializer_class = ContatoSerializer

    def get_serializer_class(self):
        return ContatoSerializer

    def get_queryset(self):
        qs = Contato.objects.filter(deleted_at__isnull=True)

        # Filtros por entidade
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        tipo = self.request.query_params.get('tipo')

        if content_type:
            qs = qs.filter(content_type_id=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)
        if tipo:
            qs = qs.filter(tipo=tipo)

        return qs.order_by('tipo', '-principal', '-created_at')

    def destroy(self, request, pk=None):
        try:
            contato = Contato.objects.get(pk=pk, deleted_at__isnull=True)
            ContatoService.delete(
                contato,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contato.DoesNotExist:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def definir_principal(self, request, pk=None):
        """Define este contato como principal do seu tipo."""
        try:
            contato = Contato.objects.get(pk=pk, deleted_at__isnull=True)
            ContatoService.definir_principal(
                contato,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(contato)
            return Response(serializer.data)
        except Contato.DoesNotExist:
            return Response(
                {'detail': 'Contato não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
