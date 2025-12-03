from django.db.models import QuerySet, Q
from rest_framework.exceptions import PermissionDenied
from ..models import Projeto, Usuario

def projeto_list(
    *,
    user: Usuario, # Adicionado parametro user
    filters: dict = None,
    search: str = None
) -> QuerySet:
    """Lista projetos ativos com filtros opcionais, respeitando permissoes regionais do usuario."""
    qs = Projeto.objects.filter(deleted_at__isnull=True).select_related('cliente__pessoa_juridica', 'filial', 'empresa__pessoa_juridica')

    if not user.is_superuser:
        qs = qs.filter(filial__in=user.allowed_filiais.all()).distinct()

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(cliente__pessoa_juridica__nome_fantasia__icontains=search) |
            Q(filial__nome__icontains=search)
        )

    return qs.order_by('nome')


def projeto_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Projeto:
    """Obtem detalhes de um projeto com relacionamentos, verificando permissao regional."""
    projeto = Projeto.objects.select_related(
        'cliente', 'filial', 'empresa',
        'cliente__pessoa_juridica', 'empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=projeto.filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso ao projeto {projeto.nome} via filial {projeto.filial.nome}.")

    return projeto
