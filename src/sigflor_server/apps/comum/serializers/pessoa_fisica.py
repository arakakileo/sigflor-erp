from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models.enums import Sexo, EstadoCivil, UF
from ..validators import validar_cpf

from .enderecos import PessoaFisicaEnderecoNestedSerializer
from .contatos import PessoaFisicaContatoNestedSerializer
from .documentos import PessoaFisicaDocumentoNestedSerializer
from .anexos import AnexoNestedSerializer
from .deficiencias import DeficienciaNestedSerializer

class PessoaFisicaCreateSerializer(serializers.Serializer):
    
    nome_completo = serializers.CharField(max_length=200)
    nome_mae = serializers.CharField(max_length=200, required=False, allow_blank=True)
    nome_pai = serializers.CharField(max_length=200, required=False, allow_blank=True)
    cpf = serializers.CharField(max_length=14)
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
    deficiencias = DeficienciaNestedSerializer(
        many=True, required=False, allow_empty=True
    )
    def validate_cpf(self, value):
        cleaned_value = ''.join(filter(str.isdigit, value))
        if not cleaned_value:
            raise serializers.ValidationError("O campo CPF é obrigatório.")
        try:
            validar_cpf(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return cleaned_value