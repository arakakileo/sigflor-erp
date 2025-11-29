from rest_framework import serializers
# Importar o novo serializer
from apps.comum.serializers.pessoa_fisica import PessoaFisicaCreateSerializer, PessoaFisicaSerializer
from ..models import Funcionario


class FuncionarioListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de funcionarios."""

    nome = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    cargo_nome = serializers.CharField(
        source='cargo.nome',
        read_only=True
    )
    empresa_nome = serializers.CharField(
        source='empresa.pessoa_juridica.razao_social',
        read_only=True
    )
    gestor_nome = serializers.CharField(
        source='gestor.pessoa_fisica.nome_completo',
        read_only=True
    )
    subcontrato_numero = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True) # Adicionado projeto_nome

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'nome',
            'cpf_formatado',
            'cargo',
            'cargo_nome',
            'departamento',
            'subcontrato',
            'subcontrato_numero',
            'filial_nome',
            'contratante_nome',
            'projeto_nome', # Adicionado projeto_nome
            'status',
            'tipo_contrato',
            'data_admissao',
            'empresa_nome',
            'gestor_nome',
        ]


class FuncionarioSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes do funcionario."""

    pessoa_fisica = PessoaFisicaSerializer(read_only=True)
    nome = serializers.ReadOnlyField()
    cpf = serializers.ReadOnlyField()
    cpf_formatado = serializers.ReadOnlyField()
    tempo_empresa = serializers.ReadOnlyField()
    is_ativo = serializers.ReadOnlyField()

    cargo_nome = serializers.CharField(
        source='cargo.nome',
        read_only=True
    )
    empresa_nome = serializers.CharField(
        source='empresa.pessoa_juridica.razao_social',
        read_only=True
    )
    gestor_nome = serializers.CharField(
        source='gestor.pessoa_fisica.nome_completo',
        read_only=True
    )
    subordinados_count = serializers.SerializerMethodField()
    subcontrato_numero = serializers.ReadOnlyField()
    filial_nome = serializers.ReadOnlyField()
    contrato_numero = serializers.ReadOnlyField()
    contratante_nome = serializers.ReadOnlyField()
    projeto_nome = serializers.CharField(source='projeto.nome', read_only=True) # Adicionado projeto_nome

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'matricula',
            'pessoa_fisica',
            'nome',
            'cpf',
            'cpf_formatado',
            # Dados profissionais
            'cargo',
            'cargo_nome',
            'departamento',
            'subcontrato',
            'subcontrato_numero',
            'filial_nome',
            'contrato_numero',
            'contratante_nome',
            'projeto', # Adicionado projeto
            'projeto_nome', # Adicionado projeto_nome
            # Dados contratuais
            'tipo_contrato',
            'data_admissao',
            'data_demissao',
            'salario',
            'tempo_empresa',
            # Jornada
            'carga_horaria_semanal',
            'turno',
            'horario_entrada',
            'horario_saida',
            # Status
            'status',
            'is_ativo',
            # Dados bancarios
            'banco',
            'agencia',
            'conta',
            'tipo_conta',
            'pix',
            # Documentos trabalhistas
            'ctps_numero',
            'ctps_serie',
            'ctps_uf',
            'pis',
            # Dependentes
            'tem_dependente',
            # Vestimenta
            'tamanho_camisa',
            'tamanho_calca',
            'tamanho_botina',
            # Vinculos
            'empresa',
            'empresa_nome',
            'gestor',
            'gestor_nome',
            'subordinados_count',
            # Outros
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'matricula', 'tempo_empresa', 'is_ativo',
            'created_at', 'updated_at'
        ]

    def get_subordinados_count(self, obj):
        return obj.subordinados.filter(deleted_at__isnull=True).count()


class FuncionarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de funcionário usando estrutura aninhada."""

    pessoa_fisica = PessoaFisicaCreateSerializer(required=True)

    class Meta:
        model = Funcionario
        fields = [
            'pessoa_fisica', 
            'matricula', 
            'cargo', 
            'departamento', 
            'subcontrato',
            'tipo_contrato', 
            'data_admissao', 
            'data_demissao', 
            'salario',
            'carga_horaria_semanal', 
            'turno', 
            'horario_entrada', 
            'horario_saida',
            'status', 
            'banco', 
            'agencia', 
            'conta', 
            'tipo_conta', 
            'pix',
            'ctps_numero', 
            'ctps_serie', 
            'ctps_uf', 
            'pis',
            'tamanho_camisa', 
            'tamanho_calca', 
            'tamanho_botina',
            'empresa', 
            'gestor', 
            'observacoes',
        ]
        extra_kwargs = {
            'matricula': {'required': False},
        }

    def create(self, validated_data):
        """
        O validated_data agora virá limpo, com um dict 'pessoa_fisica'
        contendo todos os dados pessoais e as listas aninhadas.
        """
        from apps.rh.services import FuncionarioService

        # Extrai o dicionário completo da pessoa física
        pessoa_fisica_data = validated_data.pop('pessoa_fisica')

        return FuncionarioService.create(
            pessoa_fisica_data=pessoa_fisica_data,
            created_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )

    def update(self, instance, validated_data):
        # No update, geralmente não permitimos alterar dados aninhados complexos
        # diretamente pelo endpoint do funcionário para evitar efeitos colaterais.
        # Removemos 'pessoa_fisica' se vier no payload.
        validated_data.pop('pessoa_fisica', None)

        from apps.rh.services import FuncionarioService
        return FuncionarioService.update(
            funcionario=instance,
            updated_by=self.context.get('request').user if self.context.get('request') else None,
            **validated_data
        )