# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Contrato


class ContratoSerializer(serializers.ModelSerializer):
    """Serializer completo para Contrato."""

    is_vigente = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()

    class Meta:
        model = Contrato
        fields = [
            'id',
            'numero_interno',
            'numero_externo',
            'contratante',
            'contratante_nome',
            'empresa',
            'empresa_nome',
            'descricao',
            'data_inicio',
            'data_fim',
            'ativo',
            'is_vigente',
            'valor',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_vigente', 'created_at', 'updated_at']


class ContratoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de Contrato."""

    class Meta:
        model = Contrato
        fields = [
            'numero_interno',
            'numero_externo',
            'contratante',
            'empresa',
            'descricao',
            'data_inicio',
            'data_fim',
            'ativo',
            'valor',
            'observacoes',
        ]


class ContratoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Contratos."""

    contratante_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    is_vigente = serializers.ReadOnlyField()

    class Meta:
        model = Contrato
        fields = [
            'id',
            'numero_interno',
            'numero_externo',
            'contratante_nome',
            'empresa_nome',
            'data_inicio',
            'data_fim',
            'ativo',
            'is_vigente',
        ]
