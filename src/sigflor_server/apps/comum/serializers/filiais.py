# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Filial


class FilialSerializer(serializers.ModelSerializer):
    """Serializer completo para Filial."""

    is_ativa = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()

    class Meta:
        model = Filial
        fields = [
            'id',
            'nome',
            'codigo_interno',
            'status',
            'descricao',
            'empresa',
            'empresa_nome',
            'is_ativa',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_ativa', 'created_at', 'updated_at']


class FilialCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de Filial."""

    class Meta:
        model = Filial
        fields = [
            'nome',
            'codigo_interno',
            'status',
            'descricao',
            'empresa',
        ]


class FilialListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Filiais."""

    empresa_nome = serializers.ReadOnlyField()

    class Meta:
        model = Filial
        fields = [
            'id',
            'nome',
            'codigo_interno',
            'status',
            'empresa_nome',
        ]
