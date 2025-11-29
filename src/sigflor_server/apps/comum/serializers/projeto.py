from rest_framework import serializers
from apps.comum.models import Projeto, Contratante, Filial, EmpresaCNPJ, PessoaJuridica


class ProjetoListSerializer(serializers.ModelSerializer):
    """
    Serializador para listar Projetos.
    Inclui campos de leitura para os nomes das entidades relacionadas.
    """
    cliente_nome = serializers.CharField(source='cliente.pessoa_juridica.nome_fantasia', read_only=True)
    filial_nome = serializers.CharField(source='filial.nome', read_only=True)
    empresa_nome = serializers.CharField(source='empresa.pessoa_juridica.nome_fantasia', read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'nome',
            'cliente',
            'cliente_nome',
            'filial',
            'filial_nome',
            'empresa',
            'empresa_nome',
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = ['empresa', 'created_at', 'updated_at', 'deleted_at']


class ProjetoSerializer(serializers.ModelSerializer):
    """
    Serializador completo para criação, atualização e detalhamento de Projetos.
    Permite a entrada de IDs para cliente e filial e exibe seus nomes.
    """
    cliente_nome = serializers.CharField(source='cliente.pessoa_juridica.nome_fantasia', read_only=True)
    filial_nome = serializers.CharField(source='filial.nome', read_only=True)
    empresa_nome = serializers.CharField(source='empresa.pessoa_juridica.nome_fantasia', read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'nome',
            'cliente',
            'cliente_nome',
            'filial',
            'filial_nome',
            'empresa',
            'empresa_nome',
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = ['empresa', 'created_at', 'updated_at', 'deleted_at']

    def validate(self, data):
        """
        Valida se o cliente e a filial existem e se estão ativos.
        """
        cliente_id = data.get('cliente')
        filial_id = data.get('filial')

        if cliente_id and not Contratante.objects.filter(id=cliente_id.id, deleted_at__isnull=True).exists():
            raise serializers.ValidationError({'cliente': 'Cliente não encontrado ou inativo.'})
        
        if filial_id and not Filial.objects.filter(id=filial_id.id, deleted_at__isnull=True).exists():
            raise serializers.ValidationError({'filial': 'Filial não encontrada ou inativa.'})

        return data

    def create(self, validated_data):
        # A empresa será definida automaticamente pelo método save do modelo Projeto
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # A empresa será definida automaticamente pelo método save do modelo Projeto
        return super().update(instance, validated_data)
