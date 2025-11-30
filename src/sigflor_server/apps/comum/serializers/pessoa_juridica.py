from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError

from ..models import PessoaJuridica, SituacaoCadastral
from ..validators import validar_cnpj


class PessoaJuridicaListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (sem dados aninhados)."""
    cnpj_formatado = serializers.ReadOnlyField()
    situacao_cadastral_display = serializers.CharField(
        source='get_situacao_cadastral_display', read_only=True
    )

    class Meta:
        model = PessoaJuridica
        fields = [
            'id',
            'razao_social',
            'nome_fantasia',
            'cnpj_formatado',
            'situacao_cadastral',
            'situacao_cadastral_display',
        ]


class PessoaJuridicaSerializer(serializers.ModelSerializer):
    """Serializer para leitura de Pessoa Jurídica com dados completos."""

    cnpj_formatado = serializers.ReadOnlyField()
    situacao_cadastral_display = serializers.CharField(
        source='get_situacao_cadastral_display', read_only=True
    )

    class Meta:
        model = PessoaJuridica
        fields = [
            'id',
            'razao_social',
            'nome_fantasia',
            'cnpj',
            'cnpj_formatado',
            'inscricao_estadual',
            'data_abertura',
            'situacao_cadastral',
            'situacao_cadastral_display',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'cnpj_formatado', 'situacao_cadastral_display',
            'created_at', 'updated_at'
        ]

    def validate_cnpj(self, value):
        """Remove formatação do CNPJ."""
        return ''.join(filter(str.isdigit, value))


class PessoaJuridicaCreateSerializer(serializers.Serializer):
    """Serializer para criação de Pessoa Jurídica."""

    razao_social = serializers.CharField(max_length=200)
    nome_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    cnpj = serializers.CharField(max_length=18)
    inscricao_estadual = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_abertura = serializers.DateField(required=False, allow_null=True)
    situacao_cadastral = serializers.ChoiceField(
        choices=SituacaoCadastral.choices,
        default=SituacaoCadastral.ATIVA,
        required=False
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)

    def validate_cnpj(self, value):
        """Remove formatação do CNPJ e valida."""
        cleaned_value = ''.join(filter(str.isdigit, value))
        try:
            validar_cnpj(cleaned_value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return cleaned_value


class PessoaJuridicaUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de Pessoa Jurídica."""

    razao_social = serializers.CharField(max_length=200, required=False)
    nome_fantasia = serializers.CharField(max_length=200, required=False, allow_blank=True)
    inscricao_estadual = serializers.CharField(max_length=20, required=False, allow_blank=True)
    data_abertura = serializers.DateField(required=False, allow_null=True)
    situacao_cadastral = serializers.ChoiceField(
        choices=SituacaoCadastral.choices,
        required=False
    )
    observacoes = serializers.CharField(required=False, allow_blank=True)
