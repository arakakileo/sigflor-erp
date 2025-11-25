# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Cargo, Funcionario, Dependente


# ============ Cargo ============

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'salario',
        'cbo',
        'nivel',
        'ativo',
        'funcionarios_count',
        'created_at',
    ]
    list_filter = [
        'ativo',
        'nivel',
        'created_at',
    ]
    search_fields = [
        'nome',
        'cbo',
        'descricao',
    ]
    readonly_fields = [
        'id',
        'funcionarios_count',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    ordering = ['nome']

    fieldsets = (
        ('Dados do Cargo', {
            'fields': ('id', 'nome', 'salario', 'cbo', 'nivel')
        }),
        ('Descricao', {
            'fields': ('descricao',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('ativo', 'funcionarios_count')
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Funcionario ============


class DependenteInline(admin.TabularInline):
    """Inline para exibir dependentes no formulario do funcionario."""
    model = Dependente
    extra = 0
    fields = [
        'nome_completo',
        'cpf',
        'data_nascimento',
        'parentesco',
        'incluso_ir',
        'incluso_plano_saude'
    ]
    readonly_fields = []

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = [
        'matricula',
        'get_nome',
        'get_cpf',
        'cargo',
        'departamento',
        'status',
        'tem_dependente',
        'tipo_contrato',
        'data_admissao',
        'get_empresa',
    ]
    list_filter = [
        'status',
        'cargo',
        'tem_dependente',
        'tipo_contrato',
        'turno',
        'departamento',
        'empresa',
        'created_at',
    ]
    search_fields = [
        'matricula',
        'pessoa_fisica__nome_completo',
        'pessoa_fisica__cpf',
        'cargo__nome',
    ]
    readonly_fields = [
        'id',
        'matricula',
        'tem_dependente',
        'tempo_empresa',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['pessoa_fisica', 'cargo', 'empresa', 'gestor', 'subcontrato']
    ordering = ['pessoa_fisica__nome_completo']
    inlines = [DependenteInline]

    fieldsets = (
        ('Identificacao', {
            'fields': ('id', 'matricula', 'pessoa_fisica')
        }),
        ('Dados Profissionais', {
            'fields': ('cargo', 'departamento', 'subcontrato', 'empresa')
        }),
        ('Contrato', {
            'fields': (
                'tipo_contrato',
                'data_admissao',
                'data_demissao',
                'salario',
                'tempo_empresa'
            )
        }),
        ('Jornada de Trabalho', {
            'fields': (
                'carga_horaria_semanal',
                'turno',
                'horario_entrada',
                'horario_saida'
            )
        }),
        ('Status e Dependentes', {
            'fields': ('status', 'tem_dependente')
        }),
        ('Vestimenta / Uniforme', {
            'fields': ('tamanho_camisa', 'tamanho_calca', 'tamanho_botina'),
            'classes': ('collapse',)
        }),
        ('Dados Bancarios', {
            'fields': ('banco', 'agencia', 'conta', 'tipo_conta', 'pix'),
            'classes': ('collapse',)
        }),
        ('Documentos Trabalhistas', {
            'fields': ('ctps_numero', 'ctps_serie', 'ctps_uf', 'pis'),
            'classes': ('collapse',)
        }),
        ('Hierarquia', {
            'fields': ('gestor',)
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_nome(self, obj):
        return obj.pessoa_fisica.nome_completo
    get_nome.short_description = 'Nome'
    get_nome.admin_order_field = 'pessoa_fisica__nome_completo'

    def get_cpf(self, obj):
        return obj.pessoa_fisica.cpf_formatado
    get_cpf.short_description = 'CPF'

    def get_empresa(self, obj):
        if obj.empresa:
            return obj.empresa.pessoa_juridica.razao_social
        return '-'
    get_empresa.short_description = 'Empresa'
    get_empresa.admin_order_field = 'empresa__pessoa_juridica__razao_social'


@admin.register(Dependente)
class DependenteAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo',
        'get_cpf_formatado',
        'parentesco',
        'get_funcionario',
        'get_funcionario_matricula',
        'idade',
        'incluso_ir',
        'incluso_plano_saude',
    ]
    list_filter = [
        'parentesco',
        'incluso_ir',
        'incluso_plano_saude',
        'sexo',
        'created_at',
    ]
    search_fields = [
        'nome_completo',
        'cpf',
        'funcionario__matricula',
        'funcionario__pessoa_fisica__nome_completo',
    ]
    readonly_fields = [
        'id',
        'idade',
        'cpf_formatado',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['funcionario']
    ordering = ['funcionario__pessoa_fisica__nome_completo', 'nome_completo']

    fieldsets = (
        ('Vinculo', {
            'fields': ('id', 'funcionario')
        }),
        ('Dados Pessoais', {
            'fields': (
                'nome_completo',
                'cpf',
                'cpf_formatado',
                'data_nascimento',
                'idade',
                'sexo'
            )
        }),
        ('Parentesco', {
            'fields': ('parentesco',)
        }),
        ('Beneficios', {
            'fields': ('incluso_ir', 'incluso_plano_saude')
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_funcionario(self, obj):
        return obj.funcionario.pessoa_fisica.nome_completo
    get_funcionario.short_description = 'Funcionario'
    get_funcionario.admin_order_field = 'funcionario__pessoa_fisica__nome_completo'

    def get_funcionario_matricula(self, obj):
        return obj.funcionario.matricula
    get_funcionario_matricula.short_description = 'Matricula'
    get_funcionario_matricula.admin_order_field = 'funcionario__matricula'

    def get_cpf_formatado(self, obj):
        return obj.cpf_formatado or '-'
    get_cpf_formatado.short_description = 'CPF'
