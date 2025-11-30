# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Alocacao


class AlocacaoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de alocações."""

    funcionario_nome = serializers.ReadOnlyField()
    projeto_descricao = serializers.ReadOnlyField()
    is_ativa = serializers.ReadOnlyField()
    duracao_dias = serializers.ReadOnlyField()

    class Meta:
        model = Alocacao
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'projeto',
            'projeto_descricao',
            'data_inicio',
            'data_fim',
            'is_ativa',
            'duracao_dias',
        ]


class AlocacaoSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes da alocação."""

    funcionario_nome = serializers.ReadOnlyField()
    projeto_descricao = serializers.ReadOnlyField()
    is_ativa = serializers.ReadOnlyField()
    duracao_dias = serializers.ReadOnlyField()

    class Meta:
        model = Alocacao
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'projeto',
            'projeto_descricao',
            'data_inicio',
            'data_fim',
            'observacoes',
            'is_ativa',
            'duracao_dias',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'funcionario_nome', 'projeto_descricao',
            'is_ativa', 'duracao_dias', 'created_at', 'updated_at'
        ]


class AlocacaoCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de alocação."""

    class Meta:
        model = Alocacao
        fields = [
            'funcionario',
            'projeto',
            'data_inicio',
            'data_fim',
            'observacoes',
        ]

    def create(self, validated_data):
        """Cria alocação usando o service."""
        from ..services import AlocacaoService

        return AlocacaoService.alocar_funcionario(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class AlocacaoUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de alocação."""

    class Meta:
        model = Alocacao
        fields = [
            'data_fim',
            'observacoes',
        ]

    def update(self, instance, validated_data):
        """Atualiza alocação usando o service."""
        from ..services import AlocacaoService

        data_fim = validated_data.get('data_fim')
        if data_fim and not instance.data_fim:
            # Encerrando alocação
            return AlocacaoService.encerrar_alocacao(
                alocacao=instance,
                data_fim=data_fim,
                updated_by=self.context.get('request').user if self.context.get('request') else None,
            )

        return AlocacaoService.update(
            alocacao=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )
