from rest_framework import serializers

from ..models import Anexo


class AnexoSerializer(serializers.ModelSerializer):
    """Serializer para Anexo."""

    tamanho_formatado = serializers.ReadOnlyField()
    extensao = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Anexo
        fields = [
            'id',
            'nome_original',
            'arquivo',
            'descricao',
            'tamanho',
            'tamanho_formatado',
            'mimetype',
            'extensao',
            'content_type',
            'content_type_name',
            'object_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'tamanho_formatado', 'extensao', 'content_type_name',
            'created_at', 'updated_at'
        ]

    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None
