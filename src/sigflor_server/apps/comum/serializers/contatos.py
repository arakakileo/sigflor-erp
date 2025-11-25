from rest_framework import serializers

from ..models import Contato


class ContatoSerializer(serializers.ModelSerializer):
    """Serializer para Contato."""

    valor_formatado = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Contato
        fields = [
            'id',
            'tipo',
            'valor',
            'valor_formatado',
            'principal',
            'content_type',
            'content_type_name',
            'object_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'valor_formatado', 'content_type_name', 'created_at', 'updated_at']

    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None
