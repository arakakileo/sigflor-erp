from rest_framework import serializers

from ..models import Contratante, PessoaJuridica
from .pessoa_juridica import PessoaJuridicaSerializer


class ContratanteSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Contratante."""

    pessoa_juridica = PessoaJuridicaSerializer(read_only=True)
    razao_social = serializers.ReadOnlyField()
    nome_fantasia = serializers.ReadOnlyField()
    cnpj = serializers.ReadOnlyField()
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = Contratante
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


class ContratanteCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de Contratante."""

    pessoa_juridica = PessoaJuridicaSerializer()

    class Meta:
        model = Contratante
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativo',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        pessoa_juridica_data = validated_data.pop('pessoa_juridica')
        pessoa_juridica = PessoaJuridica.objects.create(**pessoa_juridica_data)
        contratante = Contratante.objects.create(
            pessoa_juridica=pessoa_juridica,
            **validated_data
        )
        return contratante

    def update(self, instance, validated_data):
        pessoa_juridica_data = validated_data.pop('pessoa_juridica', None)
        if pessoa_juridica_data:
            for attr, value in pessoa_juridica_data.items():
                setattr(instance.pessoa_juridica, attr, value)
            instance.pessoa_juridica.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
