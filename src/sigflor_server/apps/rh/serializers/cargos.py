# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Cargo
from ..models.enums import NivelCargo
from .cargo_documento import CargoDocumentoNestedSerializer


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

    documentos_exigidos = CargoDocumentoNestedSerializer(many=True)

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'salario_base', 
            'cbo', 
            'descricao', 
            'nivel',
            'documentos_exigidos',
            'risco_fisico', 
            'risco_biologico', 
            'risco_quimico', 
            'risco_ergonomico', 
            'risco_acidente',
            'ativo',
        ]
        
        extra_kwargs = {
            'nivel': {'required': True, 'choices': NivelCargo.choices},
            'risco_fisico': {'required': False},
            'risco_biologico': {'required': False},
            'risco_quimico': {'required': False},
            'risco_ergonomico': {'required': False},
            'risco_acidente': {'required': False},
        }
    
    def validate_documentos_exigidos(self, value):

        tipos_vistos = set()
        for item in value:
            tipo = item['documento_tipo']
            
            if tipo in tipos_vistos:
                raise serializers.ValidationError(
                    f"O documento '{tipo}' foi informado mais de uma vez para este cargo."
                )
            
            tipos_vistos.add(tipo)

        return value

class CargoUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cargo
        fields = [
            'nome',
            'salario_base',
            'cbo',
            'descricao',
            'nivel',
            'risco_fisico',
            'risco_biologico',
            'risco_quimico',
            'risco_ergonomico',
            'risco_acidente',
            'ativo',
        ]
        extra_kwargs = {
            'nivel': {'required': False, 'choices': NivelCargo.choices},
        }