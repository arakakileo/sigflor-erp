from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from ..models import Endereco


class EnderecoSerializer(serializers.ModelSerializer):
    """Serializer para Endereço."""

    cep_formatado = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Endereco
        fields = [
            'id',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'cep',
            'cep_formatado',
            'pais',
            'principal',
            'content_type',
            'content_type_name',
            'object_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'cep_formatado', 'content_type_name', 'created_at', 'updated_at']

    def get_content_type_name(self, obj):
        return obj.content_type.model if obj.content_type else None

    def validate_cep(self, value):
        """Remove formatação do CEP."""
        return ''.join(filter(str.isdigit, value))
