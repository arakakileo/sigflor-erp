# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.comum.serializers import PessoaFisicaSerializer
from ..models import Funcionario


class FuncionarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de funcionarios."""

    nome = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    cargo_nome = serializers.CharField(
        source='cargo.nome',
        read_only=True
    )
    empresa_nome = serializers.CharField(
        source='empresa.pessoa_juridica.razao_social',
        read_only=True
    )
    gestor_nome = serializers.CharField(
        source='gestor.pessoa_fisica.nome_completo',
        read_only=True
    )
    subcontrato_numero = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'nome',
            'cpf_formatado',
            'cargo',
            'cargo_nome',
            'departamento',
            'subcontrato',
            'subcontrato_numero',
            'filial_nome',
            'contratante_nome',
            'status',
            'tipo_contrato',
            'data_admissao',
            'empresa_nome',
            'gestor_nome',
        ]


class FuncionarioSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do funcionario."""

    pessoa_fisica = PessoaFisicaSerializer(read_only=True)
    nome = serializers.ReadOnlyField()
    cpf = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    tempo_empresa = serializers.ReadOnlyField()
    is_ativo = serializers.ReadOnlyField()

    cargo_nome = serializers.CharField(
        source='cargo.nome',
        read_only=True
    )
    empresa_nome = serializers.CharField(
        source='empresa.pessoa_juridica.razao_social',
        read_only=True
    )
    gestor_nome = serializers.CharField(
        source='gestor.pessoa_fisica.nome_completo',
        read_only=True
    )
    subordinados_count = serializers.SerializerMethodField()
    subcontrato_numero = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contrato_numero = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'pessoa_fisica',
            'nome',
            'cpf',
            'cpf_formatado',
            # Dados profissionais
            'cargo',
            'cargo_nome',
            'departamento',
            'subcontrato',
            'subcontrato_numero',
            'filial_nome',
            'contrato_numero',
            'contratante_nome',
            # Dados contratuais
            'tipo_contrato',
            'data_admissao',
            'data_demissao',
            'salario',
            'tempo_empresa',
            # Jornada
            'carga_horaria_semanal',
            'turno',
            'horario_entrada',
            'horario_saida',
            # Status
            'status',
            'is_ativo',
            # Dados bancarios
            'banco',
            'agencia',
            'conta',
            'tipo_conta',
            'pix',
            # Documentos trabalhistas
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis',
            # Dependentes
            'tem_dependente',
            # Vestimenta
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_botina',
            # Vinculos
            'empresa',
            'empresa_nome',
            'gestor',
            'gestor_nome',
            'subordinados_count',
            # Outros
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'matricula', 'tempo_empresa', 'is_ativo',
            'created_at', 'updated_at'
        ]

    def get_subordinados_count(self, obj):
        return obj.subordinados.filter(deleted_at__isnull=True).count()


class FuncionarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criacao/edicao de funcionario."""

    # Campos da PessoaFisica para criacao inline
    nome_completo = serializers.CharField(write_only=True)
    cpf = serializers.CharField(write_only=True)
    rg = serializers.CharField(write_only=True, required=False, allow_blank=True)
    orgao_emissor = serializers.CharField(write_only=True, required=False, allow_blank=True)
    data_nascimento = serializers.DateField(write_only=True, required=False, allow_null=True)
    sexo = serializers.ChoiceField(
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        write_only=True,
        required=False,
        allow_blank=True
    )
    estado_civil = serializers.CharField(write_only=True, required=False, allow_blank=True)
    nacionalidade = serializers.CharField(write_only=True, required=False, allow_blank=True)
    naturalidade = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Funcionario
        fields = [
            # Campos PessoaFisica (write_only)
            'nome_completo',
            'cpf',
            'rg',
            'orgao_emissor',
            'data_nascimento',
            'sexo',
            'estado_civil',
            'nacionalidade',
            'naturalidade',
            # Campos Funcionario
            'pessoa_fisica',
            'matricula',
            'cargo',
            'departamento',
            'subcontrato',
            'tipo_contrato',
            'data_admissao',
            'data_demissao',
            'salario',
            'carga_horaria_semanal',
            'turno',
            'horario_entrada',
            'horario_saida',
            'status',
            'banco',
            'agencia',
            'conta',
            'tipo_conta',
            'pix',
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis',
            # Vestimenta
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_botina',
            # Vinculos
            'empresa',
            'gestor',
            'observacoes',
        ]
        extra_kwargs = {
            'pessoa_fisica': {'required': False},
            'matricula': {'required': False},
        }

    def validate_cpf(self, value):
        """Remove formatacao do CPF."""
        return ''.join(filter(str.isdigit, value))

    def create(self, validated_data):
        """Cria funcionario com PessoaFisica."""
        from apps.rh.services import FuncionarioService

        # Extrai dados da pessoa fisica
        pessoa_fisica_data = {
            'nome_completo': validated_data.pop('nome_completo', None),
            'cpf': validated_data.pop('cpf', None),
            'rg': validated_data.pop('rg', None),
            'orgao_emissor': validated_data.pop('orgao_emissor', None),
            'data_nascimento': validated_data.pop('data_nascimento', None),
            'sexo': validated_data.pop('sexo', None),
            'estado_civil': validated_data.pop('estado_civil', None),
            'nacionalidade': validated_data.pop('nacionalidade', None),
            'naturalidade': validated_data.pop('naturalidade', None),
        }

        # Remove valores None/vazios
        pessoa_fisica_data = {k: v for k, v in pessoa_fisica_data.items() if v}

        return FuncionarioService.create(
            pessoa_fisica_data=pessoa_fisica_data if pessoa_fisica_data else None,
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )

    def update(self, instance, validated_data):
        """Atualiza funcionario."""
        from apps.rh.services import FuncionarioService

        # Remove campos de pessoa fisica (nao atualiza por aqui)
        for field in ['nome_completo', 'cpf', 'rg', 'orgao_emissor',
                      'data_nascimento', 'sexo', 'estado_civil',
                      'nacionalidade', 'naturalidade']:
            validated_data.pop(field, None)

        return FuncionarioService.update(
            funcionario=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )
