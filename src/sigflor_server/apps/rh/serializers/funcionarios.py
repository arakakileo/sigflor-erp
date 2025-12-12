# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.comum.serializers.pessoa_fisica import PessoaFisicaCreateSerializer, PessoaFisicaSerializer
from .dependentes import DependenteNestedCreateSerializer
from ..models import Funcionario
from ..models.enums import (
    TipoContrato, 
    StatusFuncionario, 
    TipoConta,
    TamanhoCalca,
    TamanhoCamisa,
    TamanhoCalcado,

)
from apps.comum.models.enums import UF


class FuncionarioListSerializer(serializers.ModelSerializer):

    nome = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    cargo_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.ReadOnlyField()

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'nome',
            'cpf_formatado',
            'cargo',
            'cargo_nome',
            'empresa',
            'empresa_nome',
            'projeto',
            'projeto_nome',
            'status',
            'tipo_contrato',
            'data_admissao',
            'is_ativo',
        ]

class FuncionarioSerializer(serializers.ModelSerializer):

    pessoa_fisica = PessoaFisicaSerializer(read_only=True)
    nome = serializers.ReadOnlyField()
    cpf = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    is_ativo = serializers.ReadOnlyField()
    cargo_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.ReadOnlyField()

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'pessoa_fisica',
            'nome',
            'cpf',
            'cpf_formatado',
            # Vínculos
            'empresa',
            'empresa_nome',
            'cargo',
            'cargo_nome',
            'projeto',
            'projeto_nome',
            # Dados contratuais
            'tipo_contrato',
            'data_admissao',
            'data_demissao',
            'salario_nominal',
            # Status
            'status',
            'is_ativo',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Dependentes
            'tem_dependente',
            # Documentação trabalhista
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis_pasep',
            # Dados bancários
            'banco',
            'agencia',
            'conta_corrente',
            'tipo_conta',
            'chave_pix',
            # Uniforme
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_calcado',
            # Auditoria
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'matricula', 'is_ativo', 'tem_dependente',
            'created_at', 'updated_at'
        ]

class FuncionarioCreateSerializer(serializers.ModelSerializer):

    pessoa_fisica = PessoaFisicaCreateSerializer(required=True)
    tem_dependente = serializers.BooleanField(required=True)
    dependentes = DependenteNestedCreateSerializer(many=True, required=False)

    class Meta:
        model = Funcionario
        fields = [
            'pessoa_fisica',
            'empresa',
            'cargo',
            'projeto',
            'tipo_contrato',
            'data_admissao',
            'salario_nominal',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Documentação trabalhista
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis_pasep',
            # Dados bancários
            'banco',
            'agencia',
            'conta_corrente',
            'tipo_conta',
            'chave_pix',
            # Uniforme
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_calcado',
            'tem_dependente',
            'dependentes',
        ]
        extra_kwargs = {
            'salario_nominal': {'required': False},
            'tipo_contrato': {'choices': TipoContrato.choices},
            'ctps_uf': {'choices': UF.choices},
            'tipo_conta': {'choices': TipoConta.choices},
            'tamanho_camisa': {'choices': TamanhoCamisa.choices},
            'tamanho_calca': {'choices': TamanhoCalca.choices},
            'tamanho_calcado': {'choices': TamanhoCalcado.choices},
        }

    def validate(self, data):
        tem_dependente = data.get('tem_dependente')
        dependentes = data.get('dependentes')

        if tem_dependente is True:
            if not dependentes:
                raise serializers.ValidationError({
                    "dependentes": "A lista de dependentes é obrigatória quando 'tem_dependente' é verdadeiro."
                })

        if tem_dependente is False:
            if dependentes:
                raise serializers.ValidationError({
                    "dependentes": "Não envie dados de dependentes quando 'tem_dependente' for falso."
                })

        return data

class FuncionarioUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Funcionario
        fields = [
            'cargo',
            'projeto',
            'salario_nominal',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Documentação trabalhista
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis_pasep',
            # Dados bancários
            'banco',
            'agencia',
            'conta_corrente',
            'tipo_conta',
            'chave_pix',
            # Uniforme
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_calcado',
        ]
        extra_kwargs = {
            'tipo_contrato': {'choices': TipoContrato.choices, 'required': False},
            'status': {'choices': StatusFuncionario.choices, 'required': False},
            'ctps_uf': {'choices': UF.choices, 'required': False},
            'tipo_conta': {'choices': TipoConta.choices, 'required': False},
            'tamanho_camisa': {'choices': TamanhoCamisa.choices, 'required': False},
            'tamanho_calca': {'choices': TamanhoCalca.choices, 'required': False},
            'tamanho_calcado': {'choices': TamanhoCalcado.choices, 'required': False},
        }