# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Cargo


class CargoSerializer(serializers.ModelSerializer):
    """Serializer completo para Cargo."""

    funcionarios_count = serializers.ReadOnlyField()

    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'salario',
            'cbo',
            'descricao',
            'nivel',
            'ativo',
            'funcionarios_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'funcionarios_count', 'created_at', 'updated_at']


class CargoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de Cargo."""

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'salario',
            'cbo',
            'descricao',
            'nivel',
            'ativo',
        ]


class CargoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Cargos."""

    funcionarios_count = serializers.ReadOnlyField()

    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'salario',
            'cbo',
            'nivel',
            'ativo',
            'funcionarios_count',
        ]
