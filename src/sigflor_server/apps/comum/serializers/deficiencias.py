# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Deficiencia


class DeficienciaSerializer(serializers.ModelSerializer):
    """Serializer completo para Deficiencia."""

    pessoa_fisica_nome = serializers.CharField(
        source='pessoa_fisica.nome_completo',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )

    class Meta:
        model = Deficiencia
        fields = [
            'id',
            'pessoa_fisica',
            'pessoa_fisica_nome',
            'nome',
            'tipo',
            'tipo_display',
            'cid',
            'grau',
            'data_diagnostico',
            'congenita',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeficienciaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/atualizacao de Deficiencia."""

    class Meta:
        model = Deficiencia
        fields = [
            'pessoa_fisica',
            'nome',
            'tipo',
            'cid',
            'grau',
            'data_diagnostico',
            'congenita',
            'observacoes',
        ]


class DeficienciaListSerializer(serializers.ModelSerializer):
    """Serializer resumido para listagem de Deficiencias."""

    pessoa_fisica_nome = serializers.CharField(
        source='pessoa_fisica.nome_completo',
        read_only=True
    )
    tipo_display = serializers.CharField(
        source='get_tipo_display',
        read_only=True
    )

    class Meta:
        model = Deficiencia
        fields = [
            'id',
            'pessoa_fisica',
            'pessoa_fisica_nome',
            'nome',
            'tipo',
            'tipo_display',
            'cid',
            'congenita',
        ]
