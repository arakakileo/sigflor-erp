# -*- coding: utf-8 -*-
from rest_framework import serializers

from ..models import Equipe, EquipeFuncionario


# ============================================================================
# Equipe Serializers
# ============================================================================

class EquipeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de equipes."""

    projeto_nome = serializers.ReadOnlyField()
    lider_nome = serializers.ReadOnlyField()
    coordenador_nome = serializers.ReadOnlyField()
    membros_count = serializers.ReadOnlyField()

    class Meta:
        model = Equipe
        fields = [
            'id',
            'nome',
            'tipo_equipe',
            'projeto',
            'projeto_nome',
            'lider',
            'lider_nome',
            'coordenador',
            'coordenador_nome',
            'ativa',
            'membros_count',
        ]


class EquipeSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes da equipe."""

    projeto_nome = serializers.ReadOnlyField()
    lider_nome = serializers.ReadOnlyField()
    coordenador_nome = serializers.ReadOnlyField()
    membros_count = serializers.ReadOnlyField()

    class Meta:
        model = Equipe
        fields = [
            'id',
            'nome',
            'tipo_equipe',
            'projeto',
            'projeto_nome',
            'lider',
            'lider_nome',
            'coordenador',
            'coordenador_nome',
            'ativa',
            'observacoes',
            'membros_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'projeto_nome', 'lider_nome', 'coordenador_nome',
            'membros_count', 'created_at', 'updated_at'
        ]


class EquipeCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de equipe."""

    class Meta:
        model = Equipe
        fields = [
            'nome',
            'tipo_equipe',
            'projeto',
            'lider',
            'coordenador',
            'observacoes',
        ]

    def create(self, validated_data):
        """Cria equipe usando o service."""
        from ..services import EquipeService

        return EquipeService.criar_equipe(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class EquipeUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de equipe."""

    class Meta:
        model = Equipe
        fields = [
            'nome',
            'tipo_equipe',
            'projeto',
            'lider',
            'coordenador',
            'ativa',
            'observacoes',
        ]

    def update(self, instance, validated_data):
        """Atualiza equipe usando o service."""
        from ..services import EquipeService

        return EquipeService.update(
            equipe=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


# ============================================================================
# EquipeFuncionario Serializers
# ============================================================================

class EquipeFuncionarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de membros."""

    funcionario_nome = serializers.CharField(
        source='funcionario.nome',
        read_only=True
    )
    funcionario_matricula = serializers.CharField(
        source='funcionario.matricula',
        read_only=True
    )
    equipe_nome = serializers.CharField(
        source='equipe.nome',
        read_only=True
    )
    is_ativo = serializers.ReadOnlyField()

    class Meta:
        model = EquipeFuncionario
        fields = [
            'id',
            'equipe',
            'equipe_nome',
            'funcionario',
            'funcionario_nome',
            'funcionario_matricula',
            'data_entrada',
            'data_saida',
            'is_ativo',
        ]


class EquipeFuncionarioSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes de membro."""

    funcionario_nome = serializers.CharField(
        source='funcionario.nome',
        read_only=True
    )
    funcionario_matricula = serializers.CharField(
        source='funcionario.matricula',
        read_only=True
    )
    equipe_nome = serializers.CharField(
        source='equipe.nome',
        read_only=True
    )
    is_ativo = serializers.ReadOnlyField()

    class Meta:
        model = EquipeFuncionario
        fields = [
            'id',
            'equipe',
            'equipe_nome',
            'funcionario',
            'funcionario_nome',
            'funcionario_matricula',
            'data_entrada',
            'data_saida',
            'is_ativo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'equipe_nome', 'funcionario_nome', 'funcionario_matricula',
            'is_ativo', 'created_at', 'updated_at'
        ]


class EquipeFuncionarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para adicionar membro à equipe."""

    class Meta:
        model = EquipeFuncionario
        fields = [
            'equipe',
            'funcionario',
            'data_entrada',
        ]

    def create(self, validated_data):
        """Adiciona membro usando o service."""
        from ..services import EquipeService

        return EquipeService.adicionar_membro(
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )


class EquipeFuncionarioUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualizar/encerrar participação de membro."""

    class Meta:
        model = EquipeFuncionario
        fields = [
            'data_saida',
        ]

    def update(self, instance, validated_data):
        """Atualiza membro usando o service."""
        from ..services import EquipeService

        data_saida = validated_data.get('data_saida')
        if data_saida:
            return EquipeService.remover_membro(
                equipe_funcionario=instance,
                data_saida=data_saida,
                updated_by=self.context.get('request').user if self.context.get('request') else None,
            )

        # Atualização genérica
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_by = self.context.get('request').user if self.context.get('request') else None
        instance.save()
        return instance
