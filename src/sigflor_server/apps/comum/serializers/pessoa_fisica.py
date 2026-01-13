from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import PessoaFisica
from ..models.enums import Sexo, EstadoCivil, UF
from ..validators import validar_cpf

from .enderecos import PessoaFisicaEnderecoNestedSerializer, PessoaFisicaEnderecoSerializer
from .contatos import PessoaFisicaContatoNestedSerializer, PessoaFisicaContatoSerializer
from .documentos import PessoaFisicaDocumentoNestedSerializer, PessoaFisicaDocumentoListSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer
# from .deficiencias import DeficienciaNestedSerializer, DeficienciaListSerializer


class PessoaFisicaListSerializer(serializers.ModelSerializer):

    cpf_formatado = serializers.ReadOnlyField()

    class Meta:
        model = PessoaFisica
        fields = [
            'id',
            'nome_completo',
            'cpf_formatado',
            'nacionalidade',
            'possui_deficiencia',
        ]


class PessoaFisicaSerializer(serializers.ModelSerializer):

    cpf_formatado = serializers.ReadOnlyField()
    enderecos = PessoaFisicaEnderecoSerializer(
        many=True, read_only=True, source='enderecos_vinculados'
    )
    contatos = PessoaFisicaContatoSerializer(
        many=True, read_only=True, source='contatos_vinculados'
    )
    documentos = PessoaFisicaDocumentoListSerializer(
        many=True, read_only=True, source='documentos_vinculados'
    )
    anexos = AnexoSerializer(many=True, read_only=True) 
    # deficiencias = DeficienciaListSerializer(
    #     many=True, read_only=True
    # )

    class Meta:
        model = PessoaFisica
        fields = [
            'id',
            'nome_completo',
            'nome_mae',
            'nome_pai',
            'cpf',
            'cpf_formatado',
            'rg',
            'orgao_emissor',
            'data_nascimento',
            'sexo',
            'estado_civil',
            'nacionalidade',
            'naturalidade',
            'observacoes',
            'possui_deficiencia',
            'enderecos',
            'contatos',
            'documentos',
            'anexos',
            'deficiencias',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cpf_formatado', 'possui_deficiencia',
            'created_at', 'updated_at'
        ]


class PessoaFisicaCreateSerializer(serializers.Serializer):
    
    nome_completo = serializers.CharField(max_length=200)
    cpf = serializers.CharField(max_length=14)
    
    nome_mae = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nome_pai = serializers.CharField(max_length=200, required=False, allow_blank=True)
    rg = serializers.CharField(max_length=20, required=False, allow_blank=True)
    orgao_emissor = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_nascimento = serializers.DateField(required=False, allow_null=True)
    sexo = serializers.ChoiceField(
        choices=Sexo.choices,
        required=False,
        allow_null=True
    )
    estado_civil = serializers.ChoiceField(
        choices=EstadoCivil.choices,
        required=False,
        allow_null=True
    )
    nacionalidade = serializers.CharField(required=False, allow_blank=True)
    naturalidade = serializers.ChoiceField(
        choices=UF.choices,
        required=False, 
        allow_null=True
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)
    enderecos = PessoaFisicaEnderecoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    contatos = PessoaFisicaContatoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    documentos = PessoaFisicaDocumentoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    anexos = AnexoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    # deficiencias = DeficienciaNestedSerializer(
    #     many=True, required=False, allow_empty=True
    # )

    def validate_cpf(self, value):
        cleaned_value = ''.join(filter(str.isdigit, value))
        
        if not cleaned_value:
            raise serializers.ValidationError("O campo CPF é obrigatório.")
            
        try:
            validar_cpf(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
            
        return cleaned_value


class PessoaFisicaUpdateSerializer(serializers.Serializer):

    nome_completo = serializers.CharField(max_length=200, required=False)
    nome_mae = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nome_pai = serializers.CharField(max_length=200, required=False, allow_blank=True)
    rg = serializers.CharField(max_length=20, required=False, allow_blank=True)
    orgao_emissor = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_nascimento = serializers.DateField(required=False, allow_null=True)
    
    sexo = serializers.ChoiceField(
        choices=Sexo.choices,
        required=False,
        allow_null=True
    )
    estado_civil = serializers.ChoiceField(
        choices=EstadoCivil.choices,
        required=False,
        allow_null=True
    )
    nacionalidade = serializers.CharField(required=False, allow_blank=True)
    naturalidade = serializers.ChoiceField(
        choices=UF.choices,
        required=False, 
        allow_null=True
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)
    enderecos = PessoaFisicaEnderecoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    contatos = PessoaFisicaContatoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    documentos = PessoaFisicaDocumentoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    anexos = AnexoNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    # deficiencias = DeficienciaNestedSerializer(
    #     many=True, required=False, allow_empty=True
    # )