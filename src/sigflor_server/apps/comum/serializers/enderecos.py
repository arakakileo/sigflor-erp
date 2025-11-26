from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from ..models import Endereco


class EnderecoSerializer(serializers.ModelSerializer):
    cep_formatado = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()
    
    # CORREÇÃO DO CEP: Aumentamos o limite na entrada para aceitar a máscara (9 chars)
    # O validate_cep limpará para 8 chars antes de salvar.
    cep = serializers.CharField(max_length=9)

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
        """Remove formatação do CEP e valida se restam 8 dígitos."""
        limpo = ''.join(filter(str.isdigit, value))
        if len(limpo) != 8:
            raise serializers.ValidationError("O CEP deve conter 8 dígitos numéricos.")
        return limpo
    
class EnderecoNestedSerializer(EnderecoSerializer):
    """
    Usado quando o endereço é criado junto com a entidade pai.
    Não exige content_type/object_id pois serão inferidos pelo Service.
    """
    class Meta(EnderecoSerializer.Meta):
        # Adiciona os campos de vínculo como somente leitura para ignorar validação de entrada
        read_only_fields = EnderecoSerializer.Meta.read_only_fields + ['content_type', 'object_id']
