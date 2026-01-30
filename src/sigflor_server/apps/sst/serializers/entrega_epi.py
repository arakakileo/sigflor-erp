from rest_framework import serializers

from apps.sst.models import EntregaEPI

class EntregaEPIReadSerializer(serializers.ModelSerializer):
    """
    Serializer para leitura de Entregas de EPI.
    Expande dados do Funcionário, EPI e Tipo.
    """
    funcionario_nome = serializers.CharField(source='funcionario.nome', read_only=True)
    funcionario_cpf = serializers.CharField(source='funcionario.cpf', read_only=True)
    epi_ca = serializers.CharField(source='epi.ca', read_only=True)
    epi_nome = serializers.CharField(source='epi.tipo.nome', read_only=True)
    epi_fabricante = serializers.CharField(source='epi.fabricante', read_only=True)
    
    class Meta:
        model = EntregaEPI
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'funcionario_cpf',
            'epi',
            'epi_ca',
            'epi_nome',
            'epi_fabricante',
            'data_entrega',
            'data_validade',
            'quantidade',
            'devolvido',
            'data_devolucao',
            'observacoes',
        ]

class EntregaEPICreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de entregas.
    Foca nos IDs de entrada. Lógica de vencimento está no Service.
    """
    class Meta:
        model = EntregaEPI
        fields = [
            'funcionario',
            'epi',
            'data_entrega',
            'quantidade',
            'observacoes'
        ]
