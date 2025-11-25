from rest_framework import serializers

from ..models import PessoaFisica


class PessoaFisicaSerializer(serializers.ModelSerializer):
    """Serializer para Pessoa Física."""

    cpf_formatado = serializers.ReadOnlyField()

    class Meta:
        model = PessoaFisica
        fields = [
            'id',
            'nome_completo',
            'cpf',
            'cpf_formatado',
            'rg',
            'orgao_emissor',
            'data_nascimento',
            'sexo',
            'estado_civil',
            'nacionalidade',
            'naturalidade',
            'possui_deficiencia',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'cpf_formatado', 'created_at', 'updated_at']

    def validate_cpf(self, value):
        """Remove formatação do CPF."""
        return ''.join(filter(str.isdigit, value))
