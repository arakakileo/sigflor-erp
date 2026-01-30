from rest_framework import serializers

from apps.sst.models import TipoEPI, EPI, CargoEPI
from apps.sst.models.enums import UnidadeEPI

class TipoEPISerializer(serializers.ModelSerializer):
    unidade = serializers.ChoiceField(choices=UnidadeEPI.choices)
    
    class Meta:
        model = TipoEPI
        fields = [
            'id', 
            'nome', 
            'unidade', 
        ]


class EPISerializer(serializers.ModelSerializer):
    tipo_nome = serializers.CharField(source='tipo.nome', read_only=True)
    
    class Meta:
        model = EPI
        fields = [
            'id', 
            'tipo', 
            'tipo_nome',
            'ca', 
            'fabricante', 
            'modelo', 
            'validade_ca', 
        ]


class CargoEPISerializer(serializers.ModelSerializer):
    tipo_epi_nome = serializers.CharField(source='tipo_epi.nome', read_only=True)
    cargo_nome = serializers.CharField(source='cargo.nome', read_only=True)

    class Meta:
        model = CargoEPI
        fields = [
            'id', 
            'cargo', 
            'cargo_nome',
            'tipo_epi', 
            'tipo_epi_nome',
            'periodicidade_troca_dias', 
            'quantidade_padrao', 
            'observacoes', 
        ]


class CargoEpiNestedSerializer(serializers.ModelSerializer):
    tipo_epi_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoEPI.objects.filter(deleted_at__isnull=True),
        source='tipo_epi',
        required=True
    )
    nome = serializers.CharField(source='tipo_epi.nome', read_only=True)
    unidade = serializers.CharField(source='tipo_epi.unidade', read_only=True)
    periodicidade_troca_dias = serializers.IntegerField(required=True)
    quantidade_padrao = serializers.IntegerField(required=False, default=1)

    class Meta:
        model = CargoEPI
        fields = [
            'id', 
            'tipo_epi_id',
            'nome',
            'unidade',
            'periodicidade_troca_dias', 
            'quantidade_padrao', 
            'observacoes', 
        ]
        read_only_fields = ['id', 'nome', 'unidade']
