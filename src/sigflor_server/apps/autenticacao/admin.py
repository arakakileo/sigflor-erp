from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Usuario, Papel

# ============ Usuario ============ #

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    # CORREÇÃO 1: Trocamos 'ativo' por 'is_active'
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Adicionei os campos novos de auditoria (created_by, etc) como readonly
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'deleted_at', 
        'created_by', 'updated_by', 'deleted_by', 
        'last_login', 'date_joined'
    ]
    
    ordering = ['username']
    
    # allowed_filiais precisa estar aqui para a caixa de seleção funcionar
    filter_horizontal = ['papeis', 'user_permissions', 'allowed_filiais']

    # Organização do formulário
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        
        # CORREÇÃO 2: Removemos 'pessoa_fisica' que não existe mais
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email')}),
        
        ('Permissões de Acesso', {
            # CORREÇÃO 3: Removemos 'ativo' duplicado, mantemos apenas 'is_active'
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        
        ('RBAC Customizado (SigFlor)', {
            # Adicionei 'allowed_filiais' aqui para aparecer na tela
            'fields': ('papeis', 'user_permissions', 'allowed_filiais'),
        }),
        
        ('Auditoria e Datas', {
            'fields': (
                'last_login', 'date_joined', 
                'created_at', 'updated_at', 'deleted_at',
                'created_by', 'updated_by', 'deleted_by'
            ),
            'classes': ('collapse',)
        }),
        
        ('ID Técnico', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )

    # Configuração para o formulário de "Adicionar Usuário" (Tela inicial de create)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


# ============ Papel ============ #

@admin.register(Papel)
class PapelAdmin(admin.ModelAdmin):
    list_display = ['nome', 'get_permissoes_count', 'created_at']
    search_fields = ['nome', 'descricao']
    
    # Auditoria completa
    readonly_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    filter_horizontal = ['permissoes']
    ordering = ['nome']

    fieldsets = (
        ('Dados do Papel', {
            'fields': ('nome', 'descricao')
        }),
        ('Permissões Associadas', {
            'fields': ('permissoes',)
        }),
        ('Auditoria', {
            'fields': ('id', 'created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        }),
    )

    def get_permissoes_count(self, obj):
        return obj.permissoes.count()
    get_permissoes_count.short_description = 'Qtd. Permissões'