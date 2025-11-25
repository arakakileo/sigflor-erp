from rest_framework import serializers

from ..models import PessoaJuridica


class PessoaJuridicaSerializer(serializers.ModelSerializer):
    """Serializer para Pessoa Jurídica."""

    cnpj_formatado = serializers.ReadOnlyField()

    class Meta:
        model = PessoaJuridica
        fields = [
            'id',
            'razao_social',
            'nome_fantasia',
            'cnpj',
            'cnpj_formatado',
            'inscricao_estadual',
            'inscricao_municipal',
            'porte',
            'natureza_juridica',
            'data_abertura',
            'atividade_principal',
            'atividades_secundarias',
            'situacao_cadastral',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'cnpj_formatado', 'created_at', 'updated_at']

    def validate_cnpj(self, value):
        """Remove formatação do CNPJ."""
        return ''.join(filter(str.isdigit, value))
