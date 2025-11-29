from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import Cliente
from .pessoa_juridica import (
    PessoaJuridicaSerializer, 
    PessoaJuridicaCreateSerializer, 
    PessoaJuridicaListSerializer
)


class ClienteListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagem."""
    # Usa a versão leve da PJ
    pessoa_juridica = PessoaJuridicaListSerializer(read_only=True)
    
    class Meta:
        model = Cliente
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativo',
        ]


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Cliente."""

    pessoa_juridica = PessoaJuridicaSerializer(read_only=True)
    razao_social = serializers.ReadOnlyField()
    nome_fantasia = serializers.ReadOnlyField()
    cnpj = serializers.ReadOnlyField()
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            'id',
            'pessoa_juridica',
            'razao_social',
            'nome_fantasia',
            'cnpj',
            'cnpj_formatado',
            'descricao',
            'ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'razao_social', 'nome_fantasia', 'cnpj', 'cnpj_formatado',
            'created_at', 'updated_at'
        ]


class ClienteCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Cliente."""

    pessoa_juridica = PessoaJuridicaCreateSerializer(required=True)

    class Meta:
        model = Cliente
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativo',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        from ..services import ClienteService

        pessoa_juridica_data = validated_data.pop('pessoa_juridica')
        
        try:
            return ClienteService.create(
                pessoa_juridica_data=pessoa_juridica_data,
                created_by=self.context.get('request').user if self.context.get('request') else None,
                **validated_data
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))

    def update(self, instance, validated_data):
        
        from ..services import ClienteService
        try:
            return ClienteService.update(
                contratante=instance,
                updated_by=self.context.get('request').user if self.context.get('request') else None,
                **validated_data
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))