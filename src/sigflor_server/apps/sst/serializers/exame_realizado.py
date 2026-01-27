from rest_framework import serializers

from apps.sst.models import ExameRealizado
from apps.sst.serializers.exame import ExameSelecaoSerializer


class ExameRealizadoSerializer(serializers.ModelSerializer):
    exame_nome = serializers.CharField(source='exame.nome', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resultado_display = serializers.CharField(source='get_resultado_display', read_only=True)

    class Meta:
        model = ExameRealizado
        fields = [
            'id',
            'aso',
            'exame',
            'exame_nome',
            'status',
            'status_display',
            'resultado',
            'resultado_display',
            'data_realizacao',
            'data_validade',
            'arquivo',
            'observacoes',
        ]
        read_only_fields = ['id', 'aso', 'exame', 'exame_nome', 'status_display', 'resultado_display']


class ExameRealizadoUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ExameRealizado
        fields = [
            'status',
            'resultado',
            'data_realizacao',
            'data_validade',
            'arquivo',
            'observacoes',
        ]
