from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.comum.validators import validar_cpf

from ..models import PessoaFisica
from ..models.enums import Sexo, EstadoCivil, UF
from .enderecos import PessoaFisicaEnderecoNestedSerializer, PessoaFisicaEnderecoListSerializer
from .contatos import PessoaFisicaContatoNestedSerializer, PessoaFisicaContatoListSerializer
from .documentos import PessoaFisicaDocumentoNestedSerializer, PessoaFisicaDocumentoListSerializer
from .anexos import AnexoSerializer, AnexoNestedSerializer


class PessoaFisicaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Pessoa Física (GET)."""

    cpf_formatado = serializers.ReadOnlyField()

    # Campos aninhados para exibição completa
    enderecos = PessoaFisicaEnderecoListSerializer(many=True, read_only=True, source='enderecos_vinculados')
    contatos = PessoaFisicaContatoListSerializer(many=True, read_only=True, source='contatos_vinculados')
    documentos = PessoaFisicaDocumentoListSerializer(many=True, read_only=True, source='documentos_vinculados')
    anexos = AnexoSerializer(many=True, read_only=True) # Anexos usa GFK por exceção

    class Meta:
            model = PessoaFisica
            fields = '__all__' # (Resumido para brevidade, mantenha seus campos)

class PessoaFisicaCreateSerializer(serializers.ModelSerializer):

    enderecos = PessoaFisicaEnderecoNestedSerializer(
        many=True, required=False, allow_empty=True, source='enderecos_vinculados'
    )
    contatos = PessoaFisicaContatoNestedSerializer(
        many=True, required=False, allow_empty=True, source='contatos_vinculados'
    )
    documentos = PessoaFisicaDocumentoNestedSerializer(
        many=True, required=False, allow_empty=True, source='documentos_vinculados'
    )
    anexos = AnexoNestedSerializer(
        many=True, required=False, allow_empty=True, source='anexos_vinculados'
    )

    class Meta:
        model = PessoaFisica
        fields = [
            'nome_completo', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento',
            'sexo', 'estado_civil', 'nacionalidade', 'naturalidade', 'observacoes',
            'enderecos', 'contatos', 'documentos', 'anexos'
        ]
        extra_kwargs = {
            'cpf': {
                'max_length': 14,
                'validators': []
            },
            'sexo': {
                'required': False,
                'choices': Sexo.choices,
            },
            'estado_civil': {
                'required': False,
                'choices': EstadoCivil.choices,
            },
            'naturalidade': {
                'required': False,
                'choices': UF.choices,
            },
        }

    def validate_cpf(self, value):
        """Remove formatação do CPF e valida manualmente."""
        cleaned_value = ''.join(filter(str.isdigit, value))

        try:
            validar_cpf(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)

        return cleaned_value