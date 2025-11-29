from rest_framework import permissions


class HasPermission(permissions.BasePermission):
    """
    Permissão customizada que verifica se o usuário autenticado possui
    uma permissão específica.

    Uso: permission_classes = [HasPermission]
        permission_required = 'codigo_da_permissao' # Adicionar no ViewSet
    """
    message = 'Você não tem permissão para realizar esta ação.'

    def __init__(self, permission_code=None):
        self.permission_code = permission_code

    def has_permission(self, request, view):
        # Superusuários têm acesso total
        if request.user and request.user.is_superuser:
            return True
        
        # Se não houver código de permissão definido na view, retorna False por segurança
        # Ou permite o acesso se for apenas leitura (GET, HEAD, OPTIONS) e não houver um código específico
        if not self.permission_code:
            # Se for um método seguro e não há permissão específica requerida
            if request.method in permissions.SAFE_METHODS:
                return True
            return False

        # Verifica se o usuário tem a permissão específica
        return request.user and request.user.is_authenticated and request.user.tem_permissao(self.permission_code)

    def __call__(self):
        """
        Permite que a classe seja instanciada e usada diretamente em permission_classes,
        ex: permission_classes = [HasPermission('comum_projeto_visualizar')]
        """
        return self
