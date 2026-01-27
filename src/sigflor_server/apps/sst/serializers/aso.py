from rest_framework import serializers

from apps.rh.serializers.funcionarios import FuncionarioListSerializer
from apps.sst.models import ASO
from apps.sst.serializers.exame_realizado import ExameRealizadoSerializer


class ASOSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.CharField(source='funcionario.nome', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resultado_display = serializers.CharField(source='get_resultado_display', read_only=True)
    
    exames_realizados = ExameRealizadoSerializer(many=True, read_only=True)

    class Meta:
        model = ASO
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'tipo',
            'tipo_display',
            'status',
            'status_display',
            'resultado',
            'resultado_display',
            'data_emissao',
            'validade',
            'medico_coordenador',
            'medico_examinador',
            'observacoes',
            'exames_realizados',
            'created_at',
        ]
        read_only_fields = [
            'id', 'funcionario', 'funcionario_nome', 'status', 'created_at', 
            'exames_realizados', 'tipo_display', 'status_display', 'resultado_display'
        ]


class ASOCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ASO
        fields = ['funcionario', 'tipo']


class ASOConclusaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ASO
        fields = [
            'resultado',
            'data_emissao',
            'validade',
            'medico_coordenador',
            'medico_examinador',
            'observacoes',
        ]
        extra_kwargs = {
            'resultado': {'required': True},
            'data_emissao': {'required': True},
            'validade': {'required': True},
            'medico_coordenador': {'required': True},
            'medico_examinador': {'required': True},
        }
