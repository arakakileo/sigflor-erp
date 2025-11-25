# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import SubContrato


class SubContratoSerializer(serializers.ModelSerializer):
    """Serializer completo para SubContrato."""

    is_vigente = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contrato_numero = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()

    class Meta:
        model = SubContrato
        fields = [
            'id',
            'numero',
            'filial',
            'filial_nome',
            'contrato',
            'contrato_numero',
            'contratante_nome',
            'empresa_nome',
            'descricao',
            'data_inicio',
            'data_fim',
            'ativo',
            'is_vigente',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'numero', 'is_vigente', 'created_at', 'updated_at']


class SubContratoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de SubContrato."""

    class Meta:
        model = SubContrato
        fields = [
            'filial',
            'contrato',
            'descricao',
            'data_inicio',
            'data_fim',
            'ativo',
            'observacoes',
        ]


class SubContratoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de SubContratos."""

    filial_nome = serializers.ReadOnlyField()
    contrato_numero = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()
    is_vigente = serializers.ReadOnlyField()

    class Meta:
        model = SubContrato
        fields = [
            'id',
            'numero',
            'filial_nome',
            'contrato_numero',
            'contratante_nome',
            'data_inicio',
            'data_fim',
            'ativo',
            'is_vigente',
        ]
