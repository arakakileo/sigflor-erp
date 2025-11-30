# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.comum.serializers.pessoa_fisica import PessoaFisicaCreateSerializer, PessoaFisicaSerializer
from ..models import Funcionario


class FuncionarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de funcionários."""

    nome = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    cargo_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.ReadOnlyField()
    gestor_nome = serializers.CharField(
        source='gestor_imediato.pessoa_fisica.nome_completo',
        read_only=True
    )

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
            'turno',
            'data_admissao',
            'gestor_imediato',
            'gestor_nome',
            'is_ativo',
        ]


class FuncionarioSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do funcionário."""

    pessoa_fisica = PessoaFisicaSerializer(read_only=True)
    nome = serializers.ReadOnlyField()
    cpf = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    is_ativo = serializers.ReadOnlyField()
    cargo_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.ReadOnlyField()
    gestor_nome = serializers.CharField(
        source='gestor_imediato.pessoa_fisica.nome_completo',
        read_only=True
    )
    subordinados_count = serializers.SerializerMethodField()

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
            'turno',
            # Status
            'status',
            'is_ativo',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Hierarquia
            'gestor_imediato',
            'gestor_nome',
            'subordinados_count',
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

    def get_subordinados_count(self, obj):
        return obj.subordinados.filter(deleted_at__isnull=True).count()


class FuncionarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de funcionário usando estrutura aninhada."""

    pessoa_fisica = PessoaFisicaCreateSerializer(required=True)

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
            'turno',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Hierarquia
            'gestor_imediato',
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
            'salario_nominal': {'required': False},
        }

    def create(self, validated_data):
        from apps.rh.services import FuncionarioService

        pessoa_fisica_data = validated_data.pop('pessoa_fisica')

        return FuncionarioService.admitir_funcionario(
            pessoa_fisica_data=pessoa_fisica_data,
            funcionario_data=validated_data,
            created_by=self.context.get('request').user if self.context.get('request') else None,
        )


class FuncionarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de funcionário."""

    class Meta:
        model = Funcionario
        fields = [
            'cargo',
            'projeto',
            'salario_nominal',
            'turno',
            # Dados físicos
            'peso_corporal',
            'altura',
            # Dados adicionais
            'indicacao',
            'cidade_atual',
            # Hierarquia
            'gestor_imediato',
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

    def update(self, instance, validated_data):
        from apps.rh.services import FuncionarioService

        return FuncionarioService.update(
            funcionario=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )
