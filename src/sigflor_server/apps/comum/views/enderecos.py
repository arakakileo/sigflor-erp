from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Endereco
from ..serializers import EnderecoSerializer
from ..services import EnderecoService


class EnderecoViewSet(viewsets.ModelViewSet):
    """ViewSet para Endereco."""

    queryset = Endereco.objects.filter(deleted_at__isnull=True)
    serializer_class = EnderecoSerializer

    def get_serializer_class(self):
        return EnderecoSerializer

    def get_queryset(self):
        qs = Endereco.objects.filter(deleted_at__isnull=True)

        # Filtros por entidade
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type:
            qs = qs.filter(content_type_id=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)

        return qs.order_by('-principal', '-created_at')

    def destroy(self, request, pk=None):
        try:
            endereco = Endereco.objects.get(pk=pk, deleted_at__isnull=True)
            EnderecoService.delete(
                endereco,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Endereco.DoesNotExist:
            return Response(
                {'detail': 'Endereço não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def definir_principal(self, request, pk=None):
        """Define este endereço como principal."""
        try:
            endereco = Endereco.objects.get(pk=pk, deleted_at__isnull=True)
            EnderecoService.definir_principal(
                endereco,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(endereco)
            return Response(serializer.data)
        except Endereco.DoesNotExist:
            return Response(
                {'detail': 'Endereço não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
