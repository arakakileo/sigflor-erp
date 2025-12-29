from django.db.models import QuerySet, Q
from django.contrib.auth.models import Permission
from apps.autenticacao.models import Usuario

def permissao_list(*, user: Usuario, search: str = None) -> QuerySet:
    """
    Lista permissões disponíveis para configuração de papéis.
    Filtra permissões internas do Django para não poluir a tela.
    """
    qs = Permission.objects.select_related('content_type').all()

    apps_ignorados = [
        'admin', 'contenttypes', 'sessions', 'token_blacklist', 'authtoken'
    ]
    
    qs = qs.exclude(content_type__app_label__in=apps_ignorados)

    if search:
        qs = qs.filter(
            Q(name__icontains=search) | 
            Q(codename__icontains=search) |
            Q(content_type__model__icontains=search)
        )

    return qs.order_by('content_type__app_label', 'content_type__model', 'name')