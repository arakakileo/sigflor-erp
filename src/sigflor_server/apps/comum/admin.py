# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    PessoaFisica,
    PessoaJuridica,
    Usuario,
    Permissao,
    Papel,
    EmpresaCNPJ,
    Contratante,
    Endereco,
    Contato,
    Documento,
    Anexo,
    Deficiencia,
    Filial,
    Contrato,
)


# ============ Pessoa Fisica ============

@admin.register(PessoaFisica)
class PessoaFisicaAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'cpf_formatado', 'data_nascimento', 'sexo', 'possui_deficiencia', 'created_at']
    list_filter = ['sexo', 'estado_civil', 'possui_deficiencia', 'created_at']
    search_fields = ['nome_completo', 'cpf', 'rg']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['nome_completo']

    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento')
        }),
        ('Informacoes Adicionais', {
            'fields': ('sexo', 'estado_civil', 'nacionalidade', 'naturalidade')
        }),
        ('Deficiencia', {
            'fields': ('possui_deficiencia',)
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Pessoa Juridica ============

@admin.register(PessoaJuridica)
class PessoaJuridicaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'nome_fantasia', 'cnpj_formatado', 'situacao_cadastral', 'porte']
    list_filter = ['situacao_cadastral', 'porte', 'created_at']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['razao_social']

    fieldsets = (
        ('Dados Principais', {
            'fields': ('razao_social', 'nome_fantasia', 'cnpj')
        }),
        ('Inscricoes', {
            'fields': ('inscricao_estadual', 'inscricao_municipal')
        }),
        ('Classificacao', {
            'fields': ('porte', 'natureza_juridica', 'situacao_cadastral', 'data_abertura')
        }),
        ('Atividades', {
            'fields': ('atividade_principal', 'atividades_secundarias'),
            'classes': ('collapse',)
        }),
        ('Observacoes', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Usuario ============

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'ativo', 'is_staff', 'created_at']
    list_filter = ['ativo', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'last_login', 'date_joined']
    ordering = ['username']
    filter_horizontal = ['papeis', 'permissoes_diretas', 'groups', 'user_permissions']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informacoes Pessoais', {'fields': ('first_name', 'last_name', 'email', 'pessoa_fisica')}),
        ('Permissoes', {
            'fields': ('ativo', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('RBAC', {
            'fields': ('papeis', 'permissoes_diretas'),
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
        ('ID', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


# ============ Permissao ============

@admin.register(Permissao)
class PermissaoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'created_at']
    search_fields = ['codigo', 'nome', 'descricao']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['codigo']

    fieldsets = (
        ('Dados da Permissao', {
            'fields': ('codigo', 'nome', 'descricao')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )


# ============ Papel ============

@admin.register(Papel)
class PapelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_permissoes_count', 'created_at']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    filter_horizontal = ['permissoes']
    ordering = ['nome']

    fieldsets = (
        ('Dados do Papel', {
            'fields': ('nome', 'descricao')
        }),
        ('Permissoes', {
            'fields': ('permissoes',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_permissoes_count(self, obj):
        return obj.permissoes.count()
    get_permissoes_count.short_description = 'Qtd. Permissoes'


# ============ Empresa CNPJ ============

@admin.register(EmpresaCNPJ)
class EmpresaCNPJAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativa', 'matriz', 'created_at']
    list_filter = ['ativa', 'matriz', 'created_at']
    search_fields = ['pessoa_juridica__razao_social', 'pessoa_juridica__cnpj']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['pessoa_juridica']
    ordering = ['pessoa_juridica__razao_social']

    fieldsets = (
        ('Dados da Empresa', {
            'fields': ('pessoa_juridica', 'descricao')
        }),
        ('Status', {
            'fields': ('ativa', 'matriz')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_razao_social(self, obj):
        return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razao Social'
    get_razao_social.admin_order_field = 'pessoa_juridica__razao_social'

    def get_cnpj(self, obj):
        return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'


# ============ Contratante ============

@admin.register(Contratante)
class ContratanteAdmin(admin.ModelAdmin):
    list_display = ['get_razao_social', 'get_cnpj', 'ativo', 'created_at']
    list_filter = ['ativo', 'created_at']
    search_fields = ['pessoa_juridica__razao_social', 'pessoa_juridica__cnpj', 'pessoa_juridica__nome_fantasia']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['pessoa_juridica']
    ordering = ['pessoa_juridica__razao_social']

    fieldsets = (
        ('Dados do Contratante', {
            'fields': ('pessoa_juridica', 'descricao')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_razao_social(self, obj):
        return obj.pessoa_juridica.razao_social
    get_razao_social.short_description = 'Razao Social'
    get_razao_social.admin_order_field = 'pessoa_juridica__razao_social'

    def get_cnpj(self, obj):
        return obj.pessoa_juridica.cnpj_formatado
    get_cnpj.short_description = 'CNPJ'


# ============ Endereco ============

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ['logradouro', 'numero', 'cidade', 'estado', 'cep_formatado', 'principal', 'get_entidade']
    list_filter = ['estado', 'principal', 'created_at']
    search_fields = ['logradouro', 'bairro', 'cidade', 'cep']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Endereco', {
            'fields': ('logradouro', 'numero', 'complemento', 'bairro')
        }),
        ('Localizacao', {
            'fields': ('cidade', 'estado', 'cep', 'pais')
        }),
        ('Vinculo', {
            'fields': ('content_type', 'object_id', 'principal')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_entidade(self, obj):
        return f"{obj.content_type.model}: {obj.object_id[:8]}..."
    get_entidade.short_description = 'Entidade'


# ============ Contato ============

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'valor', 'principal', 'get_entidade', 'created_at']
    list_filter = ['tipo', 'principal', 'created_at']
    search_fields = ['valor']
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Dados do Contato', {
            'fields': ('tipo', 'valor', 'principal')
        }),
        ('Vinculo', {
            'fields': ('content_type', 'object_id')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_entidade(self, obj):
        return f"{obj.content_type.model}: {obj.object_id[:8]}..."
    get_entidade.short_description = 'Entidade'


# ============ Documento ============

@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'descricao', 'data_validade', 'vencido', 'principal', 'get_entidade']
    list_filter = ['tipo', 'principal', 'created_at']
    search_fields = ['tipo', 'descricao']
    readonly_fields = ['id', 'vencido', 'nome_arquivo', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Dados do Documento', {
            'fields': ('tipo', 'descricao', 'arquivo', 'nome_arquivo')
        }),
        ('Validade', {
            'fields': ('data_emissao', 'data_validade', 'vencido', 'principal')
        }),
        ('Vinculo', {
            'fields': ('content_type', 'object_id')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_entidade(self, obj):
        return f"{obj.content_type.model}: {obj.object_id[:8]}..."
    get_entidade.short_description = 'Entidade'


# ============ Anexo ============

@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    list_display = ['nome_original', 'mimetype', 'tamanho_formatado', 'get_entidade', 'created_at']
    list_filter = ['mimetype', 'created_at']
    search_fields = ['nome_original', 'descricao']
    readonly_fields = ['id', 'tamanho', 'tamanho_formatado', 'extensao', 'created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Dados do Anexo', {
            'fields': ('nome_original', 'arquivo', 'descricao')
        }),
        ('Metadados', {
            'fields': ('tamanho', 'tamanho_formatado', 'mimetype', 'extensao'),
            'classes': ('collapse',)
        }),
        ('Vinculo', {
            'fields': ('content_type', 'object_id')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_entidade(self, obj):
        return f"{obj.content_type.model}: {obj.object_id[:8]}..."
    get_entidade.short_description = 'Entidade'


# ============ Deficiencia ============

class DeficienciaInline(admin.TabularInline):
    """Inline para exibir deficiencias no formulario de pessoa fisica."""
    model = Deficiencia
    extra = 0
    fields = ['nome', 'tipo', 'cid', 'grau', 'congenita']
    readonly_fields = []

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


# Adiciona inline ao PessoaFisicaAdmin
PessoaFisicaAdmin.inlines = [DeficienciaInline]


@admin.register(Deficiencia)
class DeficienciaAdmin(admin.ModelAdmin):
    list_display = [
        'nome',
        'get_pessoa_nome',
        'tipo',
        'cid',
        'grau',
        'congenita',
        'created_at',
    ]
    list_filter = [
        'tipo',
        'congenita',
        'created_at',
    ]
    search_fields = [
        'nome',
        'cid',
        'pessoa_fisica__nome_completo',
        'pessoa_fisica__cpf',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    raw_id_fields = ['pessoa_fisica']
    ordering = ['pessoa_fisica__nome_completo', 'nome']

    fieldsets = (
        ('Vinculo', {
            'fields': ('id', 'pessoa_fisica')
        }),
        ('Dados da Deficiencia', {
            'fields': ('nome', 'tipo', 'cid', 'grau')
        }),
        ('Informacoes Adicionais', {
            'fields': ('data_diagnostico', 'congenita')
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

    def get_pessoa_nome(self, obj):
        return obj.pessoa_fisica.nome_completo
    get_pessoa_nome.short_description = 'Pessoa'
    get_pessoa_nome.admin_order_field = 'pessoa_fisica__nome_completo'


# ============ Filial ============

@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo_interno', 'status', 'get_empresa_nome', 'is_ativa', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['nome', 'codigo_interno', 'empresa__pessoa_juridica__razao_social']
    readonly_fields = ['id', 'is_ativa', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['empresa']
    ordering = ['nome']

    fieldsets = (
        ('Dados da Filial', {
            'fields': ('nome', 'codigo_interno', 'descricao')
        }),
        ('Vinculo', {
            'fields': ('empresa',)
        }),
        ('Status', {
            'fields': ('status', 'is_ativa')
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_empresa_nome(self, obj):
        return obj.empresa_nome
    get_empresa_nome.short_description = 'Empresa'
    get_empresa_nome.admin_order_field = 'empresa__pessoa_juridica__razao_social'


# ============ Contrato ============

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = [
        'numero_interno',
        'numero_externo',
        'get_contratante_nome',
        'get_empresa_nome',
        'data_inicio',
        'data_fim',
        'ativo',
        'is_vigente',
    ]
    list_filter = ['ativo', 'data_inicio', 'created_at']
    search_fields = [
        'numero_interno',
        'numero_externo',
        'contratante__pessoa_juridica__razao_social',
        'empresa__pessoa_juridica__razao_social',
    ]
    readonly_fields = ['id', 'is_vigente', 'created_at', 'updated_at', 'deleted_at']
    raw_id_fields = ['contratante', 'empresa']
    ordering = ['-data_inicio', 'numero_interno']

    fieldsets = (
        ('Identificacao', {
            'fields': ('numero_interno', 'numero_externo')
        }),
        ('Partes', {
            'fields': ('contratante', 'empresa')
        }),
        ('Vigencia', {
            'fields': ('data_inicio', 'data_fim', 'ativo', 'is_vigente')
        }),
        ('Valores', {
            'fields': ('valor',)
        }),
        ('Descricao', {
            'fields': ('descricao', 'observacoes'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_contratante_nome(self, obj):
        return obj.contratante_nome
    get_contratante_nome.short_description = 'Contratante'
    get_contratante_nome.admin_order_field = 'contratante__pessoa_juridica__razao_social'

    def get_empresa_nome(self, obj):
        return obj.empresa_nome
    get_empresa_nome.short_description = 'Empresa'
    get_empresa_nome.admin_order_field = 'empresa__pessoa_juridica__razao_social'
