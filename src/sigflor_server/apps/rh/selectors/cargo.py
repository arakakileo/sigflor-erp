from django.db.models import QuerySet, Q, Count

from ..models import Cargo, Funcionario, RiscoPadrao
from apps.autenticacao.models.usuarios import Usuario

# ============================================================================
# Cargo Selectors
# ============================================================================

def cargo_list(
    *,
    user:Usuario,
    busca: str = None,
    ativo: bool = None,
    cbo: str = None,
    nivel: str = None,
    com_risco: bool = None
) -> QuerySet:
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if cbo:
        qs = qs.filter(cbo__icontains=cbo)

    if nivel:
        qs = qs.filter(nivel=nivel)

    if com_risco is not None:
        if com_risco:
            # Caso TRUE: Traz quem tem PELO MENOS UM risco diferente do padrão "Ausência..."
            qs = qs.exclude(
                risco_fisico=RiscoPadrao.FISICO,
                risco_biologico=RiscoPadrao.BIOLOGICO,
                risco_quimico=RiscoPadrao.QUIMICO,
                risco_ergonomico=RiscoPadrao.ERGONOMICO,
                risco_acidente=RiscoPadrao.ACIDENTE
            )
        else:
            # Caso FALSE: Traz quem tem TODOS os riscos iguais ao padrão "Ausência..."
            qs = qs.filter(
                risco_fisico=RiscoPadrao.FISICO,
                risco_biologico=RiscoPadrao.BIOLOGICO,
                risco_quimico=RiscoPadrao.QUIMICO,
                risco_ergonomico=RiscoPadrao.ERGONOMICO,
                risco_acidente=RiscoPadrao.ACIDENTE
            )

    if busca:
        qs = qs.filter(
            Q(nome__icontains=busca) |
            Q(cbo__icontains=busca) |
            Q(descricao__icontains=busca)
        )

    return qs.order_by('nome')


def cargo_detail(*, user: Usuario, pk) -> Cargo:
    """Obtém detalhes de um cargo."""
    # Cargos são globais, não dependem de filial do usuário,
    # mas o acesso pode ser restrito por permissão na View
    return Cargo.objects.prefetch_related(
        'documentos_obrigatorios'
    ).get(pk=pk, deleted_at__isnull=True)


def cargos_ativos(*, user: Usuario) -> QuerySet:
    """Lista apenas cargos ativos."""
    return Cargo.objects.filter(
        ativo=True,
        deleted_at__isnull=True
    ).order_by('nome')


def funcionarios_por_cargo(*, user: Usuario, cargo_id: str) -> QuerySet:
    """Lista funcionários de um cargo específico."""
    qs = Funcionario.objects.filter(
        cargo_id=cargo_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'projeto')

    if not user.is_superuser:
        qs = qs.filter(
            Q(projeto__filial__in=user.allowed_filiais.all()) |
            Q(projeto__isnull=True)
        ).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_cargos(*, user: Usuario) -> dict:
    """Retorna estatísticas de cargos."""
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    ativos = qs.filter(ativo=True).count()
    com_risco = qs.filter(
        Q(risco_fisico=True) |
        Q(risco_biologico=True) |
        Q(risco_quimico=True) |
        Q(risco_ergonomico=True) |
        Q(risco_acidente=True)
    ).count()

    por_nivel = qs.filter(ativo=True).values('nivel').annotate(
        total=Count('id')
    ).order_by('nivel')

    return {
        'total_cargos': total,
        'cargos_ativos': ativos,
        'com_risco': com_risco,
        'por_nivel': list(por_nivel),
    }
