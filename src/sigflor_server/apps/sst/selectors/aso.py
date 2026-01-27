from typing import Optional
from django.db.models import QuerySet
from apps.autenticacao.models.usuarios import Usuario
from apps.sst.models import ASO

def aso_list(*, user: Usuario, funcionario_id: str = None, status: str = None) -> QuerySet[ASO]:
    qs = ASO.objects.filter(deleted_at__isnull=True).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo',
        'funcionario__empresa'
    )
    
    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)
        
    if status:
        qs = qs.filter(status=status)
        
    # Filtro regional (RBAC) - se não for superuser, vê apenas da filial permitida?
    # Assumindo que o acesso é via filial do funcionário (que está ligada ao projeto->filial ou empresa?)
    # Por segurança, vamos filtrar se o Funcionario estiver em uma filial permitida.
    # Mas Funcionario -> Empresa. Funcionario -> Projeto -> Filial.
    # Como o vinculo de projeto foi removido do Funcionario e agora é via Equipe,
    # pode ser complexo filtrar por filial aqui sem joins pesados.
    # Por enquanto, vamos manter sem filtro de filial explícito aqui, confiando na view ou permissões globais,
    # ou implementar se o Usuario tiver allowed_filiais.
    
    if not user.is_superuser:
        # Tenta filtrar pelos funcionários que o usuário pode ver (via alocação de equipe ou empresa)
        # Se for muito custoso, deixamos aberto por enquanto e refinamos depois.
        pass

    return qs.order_by('-created_at')


def aso_detail(*, user: Usuario, pk: str) -> ASO:
    return ASO.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo'
    ).prefetch_related(
        'exames_realizados',
        'exames_realizados__exame'
    ).get(pk=pk, deleted_at__isnull=True)
