from rest_framework import serializers

from ..models import EmpresaCNPJ, PessoaJuridica
from .pessoa_juridica import PessoaJuridicaSerializer


class EmpresaCNPJSerializer(serializers.ModelSerializer):
    """Serializer para leitura de EmpresaCNPJ."""

    pessoa_juridica = PessoaJuridicaSerializer(read_only=True)
    razao_social = serializers.ReadOnlyField()
    cnpj = serializers.ReadOnlyField()
    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = EmpresaCNPJ
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


class EmpresaCNPJCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de EmpresaCNPJ."""

    pessoa_juridica = PessoaJuridicaSerializer()

    class Meta:
        model = EmpresaCNPJ
        fields = [
            'id',
            'pessoa_juridica',
            'descricao',
            'ativa',
            'matriz',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        pessoa_juridica_data = validated_data.pop('pessoa_juridica')
        pessoa_juridica = PessoaJuridica.objects.create(**pessoa_juridica_data)
        empresa = EmpresaCNPJ.objects.create(
            pessoa_juridica=pessoa_juridica,
            **validated_data
        )
        return empresa

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
