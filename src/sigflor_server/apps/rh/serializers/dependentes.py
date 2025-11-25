# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Dependente


class DependenteSerializer(serializers.ModelSerializer):
    """Serializer completo para Dependente."""

    cpf_formatado = serializers.ReadOnlyField()
    idade = serializers.ReadOnlyField()
    funcionario_nome = serializers.CharField(
        source='funcionario.pessoa_fisica.nome_completo',
        read_only=True
    )
    funcionario_matricula = serializers.CharField(
        source='funcionario.matricula',
        read_only=True
    )

    class Meta:
        model = Dependente
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'funcionario_matricula',
            'nome_completo',
            'cpf',
            'cpf_formatado',
            'data_nascimento',
            'idade',
            'sexo',
            'parentesco',
            'incluso_ir',
            'incluso_plano_saude',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'cpf_formatado', 'idade', 'created_at', 'updated_at']


class DependenteCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de Dependente."""

    class Meta:
        model = Dependente
        fields = [
            'funcionario',
            'nome_completo',
            'cpf',
            'data_nascimento',
            'sexo',
            'parentesco',
            'incluso_ir',
            'incluso_plano_saude',
            'observacoes',
        ]

    def validate_cpf(self, value):
        """Remove formatacao do CPF."""
        if value:
            return ''.join(filter(str.isdigit, value))
        return value

    def create(self, validated_data):
        """Cria dependente usando o service."""
        from ..services import DependenteService

        return DependenteService.create(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )

    def update(self, instance, validated_data):
        """Atualiza dependente usando o service."""
        from ..services import DependenteService

        return DependenteService.update(
            dependente=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class DependenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de dependentes."""

    cpf_formatado = serializers.ReadOnlyField()
    idade = serializers.ReadOnlyField()

    class Meta:
        model = Dependente
        fields = [
            'id',
            'nome_completo',
            'cpf_formatado',
            'data_nascimento',
            'idade',
            'parentesco',
            'incluso_ir',
            'incluso_plano_saude',
        ]
