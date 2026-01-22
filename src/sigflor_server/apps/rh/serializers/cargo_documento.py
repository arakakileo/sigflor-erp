# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import CargoDocumento
from apps.comum.models.enums import TipoDocumento


class CargoDocumentoSerializer(serializers.ModelSerializer):

    cargo_nome = serializers.ReadOnlyField(source='cargo.nome')
    tipo_display = serializers.ReadOnlyField(source='get_documento_tipo_display')

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
            'id', 
            'cargo_nome', 
            'tipo_display', 
            'created_at', 
            'updated_at'
        ]


class CargoDocumentoNestedSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(required=False)
    documento_tipo = serializers.ChoiceField(choices=TipoDocumento.choices, required=True)

    class Meta:
        model = CargoDocumento
        fields = [
            'id',
            'documento_tipo',
            'obrigatorio',
            'condicional',
        ]
        extra_kwargs = {
            'obrigatorio': {'default': True},
            'condicional': {'required': False, 'allow_blank': True},
        }


class CargoDocumentoListSerializer(serializers.ModelSerializer):
    cargo_nome = serializers.ReadOnlyField(source='cargo.nome')
    tipo_display = serializers.ReadOnlyField(source='get_documento_tipo_display')

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


class CargoDocumentoCreateSerializer(serializers.ModelSerializer):

    documento_tipo = serializers.ChoiceField(choices=TipoDocumento.choices)

    class Meta:
        model = CargoDocumento
        fields = [
            'cargo',
            'documento_tipo',
            'obrigatorio',
            'condicional',
        ]


class CargoDocumentoUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CargoDocumento
        fields = [
            'obrigatorio',
            'condicional',
        ]