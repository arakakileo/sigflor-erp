# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.comum.serializers.pessoa_fisica import PessoaFisicaSerializer, PessoaFisicaCreateSerializer
from ..models import Dependente


class DependenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de dependentes."""

    nome_completo = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    data_nascimento = serializers.ReadOnlyField()
    idade = serializers.ReadOnlyField()

    class Meta:
        model = Dependente
        fields = [
            'id',
            'funcionario',
            'nome_completo',
            'cpf_formatado',
            'data_nascimento',
            'idade',
            'parentesco',
            'dependencia_irrf',
            'ativo',
        ]


class DependenteSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do dependente."""

    pessoa_fisica = PessoaFisicaSerializer(read_only=True)
    nome_completo = serializers.ReadOnlyField()
    cpf = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    data_nascimento = serializers.ReadOnlyField()
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
            'pessoa_fisica',
            'nome_completo',
            'cpf',
            'cpf_formatado',
            'data_nascimento',
            'idade',
            'parentesco',
            'dependencia_irrf',
            'ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'nome_completo', 'cpf', 'cpf_formatado',
            'data_nascimento', 'idade', 'created_at', 'updated_at'
        ]


class DependenteCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de dependente usando estrutura aninhada."""

    pessoa_fisica = PessoaFisicaCreateSerializer(required=True)

    class Meta:
        model = Dependente
        fields = [
            'funcionario',
            'pessoa_fisica',
            'parentesco',
            'dependencia_irrf',
        ]

    def create(self, validated_data):
        """Cria dependente usando o service."""
        from ..services import DependenteService

        pessoa_fisica_data = validated_data.pop('pessoa_fisica')
        funcionario = validated_data.pop('funcionario')

        return DependenteService.vincular_dependente(
            funcionario=funcionario,
            pessoa_fisica_data=pessoa_fisica_data,
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class DependenteUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de dependente."""

    # Adicionamos o campo aninhado para permitir edição dos dados pessoais
    pessoa_fisica = PessoaFisicaCreateSerializer(required=False)

    class Meta:
        model = Dependente
        fields = [
            'parentesco',
            'dependencia_irrf',
            'ativo',
            'pessoa_fisica', # Incluído aqui
        ]

    def update(self, instance, validated_data):
        """Atualiza dependente usando o service."""
        from ..services import DependenteService

        # Extrai os dados da pessoa física, se houver
        pessoa_fisica_data = validated_data.pop('pessoa_fisica', None)

        return DependenteService.update(
            dependente=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            pessoa_fisica_data=pessoa_fisica_data, # Passamos os dados para o service
            **validated_data
        )
