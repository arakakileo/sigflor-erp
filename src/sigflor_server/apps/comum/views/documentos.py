from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import Documento
from ..serializers import DocumentoSerializer
from ..services import DocumentoService


class DocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet para Documento."""

    queryset = Documento.objects.filter(deleted_at__isnull=True)
    serializer_class = DocumentoSerializer

    def get_serializer_class(self):
        return DocumentoSerializer

    def get_queryset(self):
        qs = Documento.objects.filter(deleted_at__isnull=True)

        # Filtros por entidade
        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        tipo = self.request.query_params.get('tipo')
        vencidos = self.request.query_params.get('vencidos')

        if content_type:
            qs = qs.filter(content_type_id=content_type)
        if object_id:
            qs = qs.filter(object_id=object_id)
        if tipo:
            qs = qs.filter(tipo=tipo)

        if vencidos is not None:
            from django.utils import timezone
            if vencidos.lower() == 'true':
                qs = qs.filter(data_validade__lt=timezone.now().date())
            else:
                from django.db.models import Q
                qs = qs.filter(
                    Q(data_validade__isnull=True) |
                    Q(data_validade__gte=timezone.now().date())
                )

        return qs.order_by('tipo', '-principal', '-created_at')

    def destroy(self, request, pk=None):
        try:
            documento = Documento.objects.get(pk=pk, deleted_at__isnull=True)
            DocumentoService.delete(
                documento,
                user=request.user if request.user.is_authenticated else None
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Documento.DoesNotExist:
            return Response(
                {'detail': 'Documento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def definir_principal(self, request, pk=None):
        """Define este documento como principal do seu tipo."""
        try:
            documento = Documento.objects.get(pk=pk, deleted_at__isnull=True)
            DocumentoService.definir_principal(
                documento,
                updated_by=request.user if request.user.is_authenticated else None
            )
            serializer = self.get_serializer(documento)
            return Response(serializer.data)
        except Documento.DoesNotExist:
            return Response(
                {'detail': 'Documento não encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Lista documentos vencidos."""
        from django.utils import timezone
        qs = Documento.objects.filter(
            deleted_at__isnull=True,
            data_validade__lt=timezone.now().date()
        ).order_by('data_validade')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def proximos_vencer(self, request):
        """Lista documentos próximos de vencer (30 dias)."""
        from django.utils import timezone
        from datetime import timedelta

        hoje = timezone.now().date()
        limite = hoje + timedelta(days=30)

        qs = Documento.objects.filter(
            deleted_at__isnull=True,
            data_validade__gte=hoje,
            data_validade__lte=limite
        ).order_by('data_validade')
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
