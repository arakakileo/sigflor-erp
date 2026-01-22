from rest_framework import serializers
from apps.autenticacao.serializers import UsuarioResumoSerializer
from ..models import Exame, CargoExame

class ExameSerializer(serializers.ModelSerializer):

    created_by = UsuarioResumoSerializer()
    updated_by = UsuarioResumoSerializer()

    class Meta:
        model = Exame
        fields = [
            'id', 
            'nome', 
            'descricao', 
            'created_at', 
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']

class ExameSelecaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exame
        fields = ['id', 'nome']

class CargoExameSerializer(serializers.ModelSerializer):
    
    exame_nome = serializers.ReadOnlyField()

    class Meta:
        model = CargoExame
        fields = [
            'id',
            'exame_id',
            'exame_nome',
            'periodicidade_meses',
            'observacoes',
        ]
        read_only_fields = ['id', 'exame_nome', 'exame']

class CargoExameNestedSerializer(serializers.ModelSerializer):
    exame_id = serializers.PrimaryKeyRelatedField(
        queryset=Exame.objects.filter(deleted_at__isnull=True),
        source='exame',
        required=True
    )
    periodicidade_meses = serializers.IntegerField(required=True)

    class Meta:
        model = CargoExame
        fields = ['exame_id', 'periodicidade_meses', 'observacoes']