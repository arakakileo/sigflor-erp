# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import CargoDocumento


class CargoDocumentoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de documentos de cargo."""

    cargo_nome = serializers.ReadOnlyField()
    tipo_display = serializers.ReadOnlyField()

    class Meta:
        model = CargoDocumento
        fields = [
            'id',
            'cargo',
            'cargo_nome',
            'documento_tipo',
            'tipo_display',
            'obrigatorio',
        ]


class CargoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do documento de cargo."""

    cargo_nome = serializers.ReadOnlyField()
    tipo_display = serializers.ReadOnlyField()

    class Meta:
        model = CargoDocumento
        fields = [
            'id',
            'cargo',
            'cargo_nome',
            'documento_tipo',
            'tipo_display',
            'obrigatorio',
            'condicional',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cargo_nome', 'tipo_display',
            'created_at', 'updated_at'
        ]


class CargoDocumentoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de documento de cargo."""

    class Meta:
        model = CargoDocumento
        fields = [
            'cargo',
            'documento_tipo',
            'obrigatorio',
            'condicional',
        ]

    def create(self, validated_data):
        """Cria documento de cargo usando o service."""
        from ..services import CargoDocumentoService

        return CargoDocumentoService.configurar_documento_para_cargo(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class CargoDocumentoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de documento de cargo."""

    class Meta:
        model = CargoDocumento
        fields = [
            'obrigatorio',
            'condicional',
        ]

    def update(self, instance, validated_data):
        """Atualiza documento de cargo usando o service."""
        from ..services import CargoDocumentoService

        return CargoDocumentoService.update(
            cargo_documento=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )
