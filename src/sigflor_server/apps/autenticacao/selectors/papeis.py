from django.db.models import QuerySet, Q
from ..models import Papel
from apps.autenticacao.models import Usuario

def papel_list(*, user: Usuario, search: str = None) -> QuerySet:
    """
    Lista papeis ativos com suas permissões pré-carregadas.
    """

    qs = Papel.objects.filter(deleted_at__isnull=True).prefetch_related('permissoes')

    if search:
        qs = qs.filter(Q(nome__icontains=search) | Q(descricao__icontains=search))

    return qs.order_by('nome')

def usuarios_por_papel(*, user: Usuario, papel: Papel) -> QuerySet:
    """
    Lista todos os usuários vinculados a um papel específico.
    """
    qs = Usuario.objects.filter(
        papeis=papel, 
        deleted_at__isnull=True
    )
    qs = qs.select_related('pessoa_fisica')

    return qs.order_by('pessoa_fisica__nome_completo')