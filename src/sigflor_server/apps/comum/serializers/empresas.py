from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import Empresa
from .pessoa_juridica import (
    PessoaJuridicaSerializer, 
    PessoaJuridicaCreateSerializer, 
    PessoaJuridicaListSerializer
)


class EmpresaListSerializer(serializers.ModelSerializer):

    pessoa_juridica = PessoaJuridicaListSerializer(read_only=True)
    
    razao_social = serializers.ReadOnlyField()
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = Empresa
        fields = [
            'id',
            'pessoa_juridica',
            'razao_social',
            'cnpj_formatado',
            'descricao',
            'ativa',
            'matriz',
        ]


class EmpresaSerializer(serializers.ModelSerializer):
    pessoa_juridica = PessoaJuridicaSerializer(read_only=True)
    razao_social = serializers.ReadOnlyField()
    cnpj = serializers.ReadOnlyField()
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = Empresa
        fields = [
            'id',
            'pessoa_juridica',
            'razao_social',
            'cnpj',
            'cnpj_formatado',
            'descricao',
            'ativa',
            'matriz',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'razao_social', 'cnpj', 'cnpj_formatado', 'created_at', 'updated_at']


class EmpresaCreateSerializer(serializers.ModelSerializer):
    pessoa_juridica = PessoaJuridicaCreateSerializer(required=True)

    class Meta:
        model = Empresa
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativa',
            'matriz',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        from ..services import EmpresaService

        pessoa_juridica_data = validated_data.pop('pessoa_juridica')
        
        try:
            return EmpresaService.create(
                pessoa_juridica_data=pessoa_juridica_data,
                created_by=self.context.get('request').user if self.context.get('request') else None,
                **validated_data
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))

    def update(self, instance, validated_data):

        from ..services import EmpresaService
        try:
            return EmpresaService.update(
                empresa=instance,
                updated_by=self.context.get('request').user if self.context.get('request') else None,
                **validated_data
            )
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict if hasattr(e, 'message_dict') else list(e.messages))