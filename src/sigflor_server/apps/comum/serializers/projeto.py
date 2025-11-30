from rest_framework import serializers

from ..models import Projeto, StatusProjeto, Cliente, Filial, Contrato


class ProjetoListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagem de Projetos."""

    cliente_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Projeto
        fields = [
            'id',
            'numero',
            'descricao',
            'cliente',
            'cliente_nome',
            'empresa',
            'empresa_nome',
            'filial',
            'filial_nome',
            'status',
            'status_display',
            'data_inicio',
            'data_fim',
        ]


class ProjetoSerializer(serializers.ModelSerializer):
    """Serializer completo para leitura de Projeto."""

    cliente_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contrato_numero = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_ativo = serializers.ReadOnlyField()

    class Meta:
        model = Projeto
        fields = [
            'id',
            'numero',
            'descricao',
            'cliente',
            'cliente_nome',
            'empresa',
            'empresa_nome',
            'filial',
            'filial_nome',
            'contrato',
            'contrato_numero',
            'data_inicio',
            'data_fim',
            'status',
            'status_display',
            'is_ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'numero', 'empresa', 'cliente_nome', 'empresa_nome',
            'filial_nome', 'contrato_numero', 'status_display', 'is_ativo',
            'created_at', 'updated_at'
        ]


class ProjetoCreateSerializer(serializers.Serializer):
    """Serializer para criação de Projeto."""

    descricao = serializers.CharField()
    cliente_id = serializers.UUIDField()
    filial_id = serializers.UUIDField()
    contrato_id = serializers.UUIDField(required=False, allow_null=True)
    data_inicio = serializers.DateField()
    data_fim = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=StatusProjeto.choices,
        default=StatusProjeto.PLANEJADO
    )

    def validate_cliente_id(self, value):
        """Valida se o cliente existe e está ativo."""
        if not Cliente.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Cliente não encontrado ou inativo.")
        return value

    def validate_filial_id(self, value):
        """Valida se a filial existe e está ativa."""
        if not Filial.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Filial não encontrada ou inativa.")
        return value

    def validate_contrato_id(self, value):
        """Valida se o contrato existe e está ativo."""
        if value and not Contrato.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Contrato não encontrado ou inativo.")
        return value

    def validate(self, data):
        """Valida datas."""
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        if data_fim and data_inicio and data_fim < data_inicio:
            raise serializers.ValidationError({
                'data_fim': "Data de término não pode ser anterior à data de início."
            })

        return data


class ProjetoUpdateSerializer(serializers.Serializer):
    """Serializer para atualização de Projeto."""

    descricao = serializers.CharField(required=False)
    filial_id = serializers.UUIDField(required=False)
    contrato_id = serializers.UUIDField(required=False, allow_null=True)
    data_inicio = serializers.DateField(required=False)
    data_fim = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=StatusProjeto.choices, required=False)

    def validate_filial_id(self, value):
        """Valida se a filial existe e está ativa."""
        if value and not Filial.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Filial não encontrada ou inativa.")
        return value

    def validate_contrato_id(self, value):
        """Valida se o contrato existe e está ativo."""
        if value and not Contrato.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Contrato não encontrado ou inativo.")
        return value

    def validate(self, data):
        """Valida datas."""
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        # Se ambas são fornecidas, validar
        if data_fim and data_inicio and data_fim < data_inicio:
            raise serializers.ValidationError({
                'data_fim': "Data de término não pode ser anterior à data de início."
            })

        return data
