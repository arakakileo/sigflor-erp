from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission

class RbacBackend(ModelBackend):
    """
    Backend de autenticação customizado que ensina o Django a olhar
    as permissões dentro da entidade 'Papel' customizada.
    """

    def _get_group_permissions(self, user_obj):
        """
        Sobrescreve a lógica padrão que busca em 'user.groups'.
        Agora busca em 'user.papeis'.
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        if not hasattr(user_obj, '_papel_perm_cache'):
            # A MÁGICA ACONTECE AQUI:
            # Buscamos as permissões através do relacionamento 'papeis'
            # Filtrando apenas papeis ativos (deleted_at=None e ativo=True)
            perms = Permission.objects.filter(
                papel__usuario=user_obj,     # Reverse lookup do ManyToMany
                papel__deleted_at__isnull=True
            ).values_list('content_type__app_label', 'codename')
            
            user_obj._papel_perm_cache = {
                f"{app_label}.{codename}" for app_label, codename in perms
            }

        return user_obj._papel_perm_cache

    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
            
        if not hasattr(user_obj, '_all_permissions_cache'):
            user_obj._all_permissions_cache = {
                *self.get_user_permissions(user_obj),
                *self._get_group_permissions(user_obj),
            }
        
        return user_obj._all_permissions_cache