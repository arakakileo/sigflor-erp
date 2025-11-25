from rest_framework import serializers

from ..models import Documento


class DocumentoSerializer(serializers.ModelSerializer):
    """Serializer para Documento."""

    nome_arquivo = serializers.ReadOnlyField()
    vencido = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Documento
        fields = [
            'id',
            'tipo',
            'descricao',
            'arquivo',
            'nome_arquivo',
            'data_emissao',
            'data_validade',
            'vencido',
            'principal',
            'content_type',
            'content_type_name',
            'object_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'nome_arquivo', 'vencido', 'content_type_name',
            'created_at', 'updated_at'
        ]

    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None
