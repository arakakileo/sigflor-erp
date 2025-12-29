from rest_framework import serializers

from ..models import Projeto, Cliente, Filial
from ..models.enums import StatusProjeto


class ProjetoListSerializer(serializers.ModelSerializer):

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

    cliente_nome = serializers.ReadOnlyField()
    empresa_nome = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
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
            'filial_nome', 'status_display', 'is_ativo',
            'created_at', 'updated_at'
        ]

class ProjetoCreateSerializer(serializers.Serializer):

    descricao = serializers.CharField()
    cliente_id = serializers.UUIDField()
    filial_id = serializers.UUIDField()
    data_inicio = serializers.DateField()
    data_fim = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(
        choices=StatusProjeto.choices,
        default=StatusProjeto.PLANEJADO
    )

    def validate_cliente_id(self, value):
        if not Cliente.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Cliente não encontrado ou inativo.")
        return value

    def validate_filial_id(self, value):
        if not Filial.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Filial não encontrada ou inativa.")
        return value

    def validate(self, data):
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        if data_fim and data_inicio and data_fim < data_inicio:
            raise serializers.ValidationError({
                'data_fim': "Data de término não pode ser anterior à data de início."
            })

        return data

class ProjetoUpdateSerializer(serializers.Serializer):

    descricao = serializers.CharField(required=False)
    filial_id = serializers.UUIDField(required=False)
    data_inicio = serializers.DateField(required=False)
    data_fim = serializers.DateField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=StatusProjeto.choices, required=False)

    def validate_filial_id(self, value):
        if value and not Filial.objects.filter(id=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Filial não encontrada ou inativa.")
        return value

    def validate(self, data):
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')

        # Se ambas são fornecidas, validar
        if data_fim and data_inicio and data_fim < data_inicio:
            raise serializers.ValidationError({
                'data_fim': "Data de término não pode ser anterior à data de início."
            })

        return data
