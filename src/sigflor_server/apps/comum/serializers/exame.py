from rest_framework import serializers
from apps.comum.models import Exame


class ExameSerializer(serializers.ModelSerializer):
    """
    Serializador para o modelo Exame.
    """
    class Meta:
        model = Exame
        fields = [
            'id',
            'nome',
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'deleted_at']
