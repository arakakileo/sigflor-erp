from rest_framework import serializers

from ..models import Permissao, Papel


class PermissaoSerializer(serializers.ModelSerializer):
    """Serializer para Permissão."""

    class Meta:
        model = Permissao
        fields = [
            'id',
            'codigo',
            'nome',
            'descricao',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PapelSerializer(serializers.ModelSerializer):
    """Serializer para Papel (Role)."""

    permissoes = PermissaoSerializer(many=True, read_only=True)
    permissoes_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permissao.objects.all(),
        many=True,
        write_only=True,
        source='permissoes',
        required=False
    )

    class Meta:
        model = Papel
        fields = [
            'id',
            'nome',
            'descricao',
            'permissoes',
            'permissoes_ids',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
