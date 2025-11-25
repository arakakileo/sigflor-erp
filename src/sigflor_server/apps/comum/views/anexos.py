from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from ..models import Anexo
from ..serializers import AnexoSerializer
from ..services import AnexoService


class AnexoViewSet(viewsets.ModelViewSet):
    """ViewSet para Anexo."""

    queryset = Anexo.objects.filter(deleted_at__isnull=True)
    serializer_class = AnexoSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        return AnexoSerializer

    def get_queryset(self):
        qs = Anexo.objects.filter(deleted_at__isnull=True)

        # Filtros por entidade
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        mimetype = self.request.query_params.get('mimetype')

        if content_type:
            qs = qs.filter(content_type_id=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)
        if mimetype:
            qs = qs.filter(mimetype__startswith=mimetype)

        return qs.order_by('-created_at')

    def destroy(self, request, pk=None):
        try:
            anexo = Anexo.objects.get(pk=pk, deleted_at__isnull=True)
            AnexoService.delete(
                anexo,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Anexo.DoesNotExist:
            return Response(
                {'detail': 'Anexo não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )
