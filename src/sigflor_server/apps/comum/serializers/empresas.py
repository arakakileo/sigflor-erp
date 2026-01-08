from rest_framework import serializers

from ..models import Empresa
from .pessoa_juridica import (
    PessoaJuridicaSerializer, 
    PessoaJuridicaCreateSerializer,
    PessoaJuridicaUpdateSerializer
)


class EmpresaListSerializer(serializers.ModelSerializer):
    razao_social = serializers.ReadOnlyField()
    cnpj = serializers.ReadOnlyField()

    class Meta:
        model = Empresa
        fields = [
            'id',
            'razao_social',
            'cnpj',
            'descricao',
            'ativa',
        ]

class EmpresaSerializer(serializers.ModelSerializer):
    pessoa_juridica = PessoaJuridicaSerializer(read_only=True)

    class Meta:
        model = Empresa
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativa',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'razao_social', 'cnpj', 'created_at', 'updated_at']

class EmpresaCreateSerializer(serializers.ModelSerializer):
    pessoa_juridica = PessoaJuridicaCreateSerializer(required=True)

    class Meta:
        model = Empresa
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativa',
        ]
        read_only_fields = ['id']

class EmpresaUpdateSerializer(serializers.ModelSerializer):
    pessoa_juridica = PessoaJuridicaUpdateSerializer(required=True)

    class Meta:
        model = Empresa
        fields = [
            'pessoa_juridica',
            'descricao',
        ]

    def validate(self, attrs):
        if 'ativa' in self.initial_data or 'ativo' in self.initial_data:
            raise serializers.ValidationError({
                "ativa": "Para ativar ou desativar empresas use as rotas específicas de ativação/desativação."
            })
            
        return attrs

class EmpresaSelecaoSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source='pessoa_juridica.razao_social', read_only=True)
    cnpj = serializers.CharField(source='pessoa_juridica.cnpj_formatado', read_only=True)

    class Meta:
        model = Empresa
        fields = ['id', 'label', 'cnpj']