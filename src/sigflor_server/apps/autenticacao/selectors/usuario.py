from django.db.models import QuerySet, Q
from apps.autenticacao.models import Usuario

def usuario_list(*, user: Usuario, busca: str = None, ativo: bool = None, papel_id: str = None) -> QuerySet:
    qs = Usuario.objects.filter(deleted_at__isnull=True)
    qs = qs.prefetch_related('papeis', 'allowed_filiais')
    if busca:
        qs = qs.filter(
            Q(username__icontains=busca) |
            Q(email__icontains=busca) |
            Q(first_name__icontains=busca)
        )

    if ativo is not None:
        eh_ativo = str(ativo).lower() == 'true'
        qs = qs.filter(ativo=eh_ativo)

    if papel_id:
        qs = qs.filter(papeis__id=papel_id)

    return qs.order_by('first_name')