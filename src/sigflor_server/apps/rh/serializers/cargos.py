# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Cargo
from ..models.enums import NivelCargo


class CargoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de Cargos."""

    funcionarios_count = serializers.ReadOnlyField()
    tem_risco = serializers.ReadOnlyField()

    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'salario_base',
            'cbo',
            'nivel',
            'ativo',
            'tem_risco',
            'funcionarios_count',
        ]

class CargoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do Cargo."""

    funcionarios_count = serializers.ReadOnlyField()
    tem_risco = serializers.ReadOnlyField()

    class Meta:
        model = Cargo
        fields = [
            'id',
            'nome',
            'salario_base',
            'cbo',
            'descricao',
            'nivel',
            # Riscos ocupacionais
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            'tem_risco',
            # Status
            'ativo',
            'funcionarios_count',
            # Auditoria
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'funcionarios_count', 'tem_risco',
            'created_at', 'updated_at'
        ]

class CargoCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'salario_base',
            'cbo',
            'descricao',
            'nivel',
            # Riscos ocupacionais
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            # Status
            'ativo',
        ]
        extra_kwargs = {
            'nivel': {'required': True, 'choices': NivelCargo.choices},
        }

    def create(self, validated_data):
        """Cria cargo usando o service."""
        from ..services import CargoService

        return CargoService.create(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )

class CargoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de Cargo."""

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'salario_base',
            'cbo',
            'descricao',
            'nivel',
            # Riscos ocupacionais
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            # Status
            'ativo',
        ]
        extra_kwargs = {
            'nivel': {'required': False, 'choices': NivelCargo.choices},
        }

    def update(self, instance, validated_data):
        """Atualiza cargo usando o service."""
        from ..services import CargoService

        return CargoService.update(
            cargo=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )
