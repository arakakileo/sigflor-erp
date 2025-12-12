# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.comum.serializers.pessoa_fisica import PessoaFisicaSerializer, PessoaFisicaCreateSerializer
from ..models import Dependente
from ..models.enums import Parentesco


class DependenteListSerializer(serializers.ModelSerializer):

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


class DependenteNestedCreateSerializer(serializers.ModelSerializer):

    pessoa_fisica = PessoaFisicaCreateSerializer(required=True)

    class Meta:
        model = Dependente
        fields = [
            'pessoa_fisica',
            'parentesco',
            'dependencia_irrf',
        ]
        extra_kwargs = {
            'parentesco': {'choices': Parentesco.choices}
        }

class DependenteUpdateSerializer(serializers.ModelSerializer):

    pessoa_fisica = PessoaFisicaCreateSerializer(required=False)

    class Meta:
        model = Dependente
        fields = [
            'parentesco',
            'dependencia_irrf',
            'ativo',
            'pessoa_fisica',
        ]
        extra_kwargs = {
            'parentesco': {'choices': Parentesco.choices}
        }