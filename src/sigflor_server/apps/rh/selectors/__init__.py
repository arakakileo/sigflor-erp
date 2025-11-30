# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas do módulo RH.
"""
from django.db.models import QuerySet, Q, Count
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from ..models import Cargo, CargoDocumento, Funcionario, Dependente, Equipe, EquipeFuncionario, Alocacao
from apps.comum.models.usuarios import Usuario


# ============================================================================
# Funcionário Selectors
# ============================================================================

def funcionario_list(
    *,
    user: Usuario,
    busca: str = None,
    status: str = None,
    tipo_contrato: str = None,
    empresa_id: str = None,
    gestor_id: str = None,
    cargo_id: str = None,
    projeto_id: str = None,
    apenas_ativos: bool = False
) -> QuerySet:
    """Lista funcionários com filtros opcionais, respeitando permissões regionais."""
    qs = Funcionario.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'gestor_imediato',
        'gestor_imediato__pessoa_fisica',
        'projeto',
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativos:
        qs = qs.filter(status=Funcionario.Status.ATIVO)

    if status:
        qs = qs.filter(status=status)

    if tipo_contrato:
        qs = qs.filter(tipo_contrato=tipo_contrato)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if gestor_id:
        qs = qs.filter(gestor_imediato_id=gestor_id)

    if cargo_id:
        qs = qs.filter(cargo_id=cargo_id)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    if busca:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=busca) |
            Q(pessoa_fisica__cpf__icontains=busca) |
            Q(matricula__icontains=busca) |
            Q(cargo__nome__icontains=busca)
        )

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionario_detail(*, user: Usuario, pk) -> Funcionario:
    """Obtém detalhes de um funcionário com relacionamentos."""
    funcionario = Funcionario.objects.select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'gestor_imediato',
        'gestor_imediato__pessoa_fisica',
        'projeto',
    ).prefetch_related(
        'pessoa_fisica__enderecos__endereco',
        'pessoa_fisica__contatos__contato',
        'pessoa_fisica__documentos__documento',
        'subordinados',
        'subordinados__pessoa_fisica',
        'dependentes',
        'dependentes__pessoa_fisica',
        'alocacoes',
        'alocacoes_equipe',
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if funcionario.projeto and not user.allowed_filiais.filter(id=funcionario.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso a este funcionário.")

    return funcionario


def funcionarios_por_empresa(*, user: Usuario, empresa_id: str) -> QuerySet:
    """Lista funcionários de uma empresa específica."""
    qs = Funcionario.objects.filter(
        empresa_id=empresa_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_projeto(*, user: Usuario, projeto_id: str) -> QuerySet:
    """Lista funcionários de um projeto específico."""
    qs = Funcionario.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_ativos(*, user: Usuario) -> QuerySet:
    """Lista apenas funcionários ativos."""
    qs = Funcionario.objects.filter(
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_afastados(*, user: Usuario) -> QuerySet:
    """Lista funcionários afastados (afastado, férias)."""
    qs = Funcionario.objects.filter(
        status__in=[Funcionario.Status.AFASTADO, Funcionario.Status.FERIAS],
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_admitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionários admitidos em um período."""
    qs = Funcionario.objects.filter(
        data_admissao__gte=data_inicio,
        data_admissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_admissao')


def funcionarios_demitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionários demitidos em um período."""
    qs = Funcionario.objects.filter(
        data_demissao__gte=data_inicio,
        data_demissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_demissao')


def aniversariantes_mes(*, user: Usuario, mes: int = None) -> QuerySet:
    """Lista funcionários que fazem aniversário no mês."""
    if mes is None:
        mes = timezone.now().month

    qs = Funcionario.objects.filter(
        pessoa_fisica__data_nascimento__month=mes,
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__data_nascimento__day')


def subordinados_diretos(*, user: Usuario, gestor_id: str) -> QuerySet:
    """Lista subordinados diretos de um gestor."""
    qs = Funcionario.objects.filter(
        gestor_imediato_id=gestor_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_rh(*, user: Usuario) -> dict:
    """Retorna estatísticas gerais do RH."""
    qs = Funcionario.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    total = qs.count()
    ativos = qs.filter(status=Funcionario.Status.ATIVO).count()
    afastados = qs.filter(status__in=[
        Funcionario.Status.AFASTADO,
        Funcionario.Status.FERIAS
    ]).count()

    por_tipo_contrato = qs.filter(
        status=Funcionario.Status.ATIVO
    ).values('tipo_contrato').annotate(
        total=Count('id')
    ).order_by('-total')

    por_cargo = qs.filter(
        status=Funcionario.Status.ATIVO
    ).values('cargo__nome').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    return {
        'total': total,
        'ativos': ativos,
        'afastados': afastados,
        'por_tipo_contrato': list(por_tipo_contrato),
        'por_cargo': list(por_cargo),
    }


# ============================================================================
# Dependente Selectors
# ============================================================================

def dependente_list(
    *,
    user: Usuario,
    funcionario_id: str = None,
    busca: str = None,
    parentesco: str = None,
    dependencia_irrf: bool = None,
    apenas_ativos: bool = True
) -> QuerySet:
    """Lista dependentes com filtros opcionais."""
    qs = Dependente.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'pessoa_fisica'
    )

    if not user.is_superuser:
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativos:
        qs = qs.filter(ativo=True)

    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)

    if parentesco:
        qs = qs.filter(parentesco=parentesco)

    if dependencia_irrf is not None:
        qs = qs.filter(dependencia_irrf=dependencia_irrf)

    if busca:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=busca) |
            Q(pessoa_fisica__cpf__icontains=busca)
        )

    return qs.order_by('funcionario__pessoa_fisica__nome_completo', 'pessoa_fisica__nome_completo')


def dependente_detail(*, user: Usuario, pk) -> Dependente:
    """Obtém detalhes de um dependente."""
    dependente = Dependente.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__projeto',
        'pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if dependente.funcionario.projeto and not user.allowed_filiais.filter(
            id=dependente.funcionario.projeto.filial_id
        ).exists():
            raise PermissionDenied("Usuário não tem acesso a este dependente.")

    return dependente


def dependentes_por_funcionario(*, user: Usuario, funcionario_id: str) -> QuerySet:
    """Lista dependentes de um funcionário específico."""
    qs = Dependente.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_com_dependentes(*, user: Usuario) -> QuerySet:
    """Lista funcionários que possuem dependentes."""
    qs = Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_dependentes(*, user: Usuario) -> dict:
    """Retorna estatísticas de dependentes."""
    qs = Dependente.objects.filter(deleted_at__isnull=True, ativo=True)

    if not user.is_superuser:
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

    total = qs.count()
    irrf = qs.filter(dependencia_irrf=True).count()

    por_parentesco = qs.values('parentesco').annotate(
        total=Count('id')
    ).order_by('-total')

    funcionarios_qs = Funcionario.objects.filter(tem_dependente=True, deleted_at__isnull=True)
    if not user.is_superuser:
        funcionarios_qs = funcionarios_qs.filter(projeto__filial__in=user.allowed_filiais.all())
    funcionarios_com_dep = funcionarios_qs.count()

    return {
        'total_dependentes': total,
        'irrf': irrf,
        'por_parentesco': list(por_parentesco),
        'funcionarios_com_dependentes': funcionarios_com_dep,
    }


# ============================================================================
# Cargo Selectors
# ============================================================================

def cargo_list(
    *,
    user: Usuario,
    busca: str = None,
    ativo: bool = None,
    cbo: str = None,
    nivel: str = None,
    com_risco: bool = None
) -> QuerySet:
    """Lista cargos com filtros opcionais."""
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if cbo:
        qs = qs.filter(cbo__icontains=cbo)

    if nivel:
        qs = qs.filter(nivel=nivel)

    if com_risco is not None:
        if com_risco:
            qs = qs.filter(
                Q(risco_fisico=True) |
                Q(risco_biologico=True) |
                Q(risco_quimico=True) |
                Q(risco_ergonomico=True) |
                Q(risco_acidente=True)
            )
        else:
            qs = qs.filter(
                risco_fisico=False,
                risco_biologico=False,
                risco_quimico=False,
                risco_ergonomico=False,
                risco_acidente=False
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
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

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


# ============================================================================
# CargoDocumento Selectors
# ============================================================================

def cargo_documento_list(*, user: Usuario, cargo_id: str = None, apenas_obrigatorios: bool = False) -> QuerySet:
    """Lista documentos de cargo."""
    qs = CargoDocumento.objects.filter(deleted_at__isnull=True).select_related('cargo')

    if cargo_id:
        qs = qs.filter(cargo_id=cargo_id)

    if apenas_obrigatorios:
        qs = qs.filter(obrigatorio=True)

    return qs.order_by('cargo__nome', 'documento_tipo')


# ============================================================================
# Equipe Selectors
# ============================================================================

def equipe_list(
    *,
    user: Usuario,
    busca: str = None,
    projeto_id: str = None,
    tipo_equipe: str = None,
    apenas_ativas: bool = True
) -> QuerySet:
    """Lista equipes com filtros opcionais."""
    qs = Equipe.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'projeto',
        'lider',
        'lider__pessoa_fisica',
        'coordenador',
        'coordenador__pessoa_fisica'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativas:
        qs = qs.filter(ativa=True)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    if tipo_equipe:
        qs = qs.filter(tipo_equipe=tipo_equipe)

    if busca:
        qs = qs.filter(
            Q(nome__icontains=busca) |
            Q(projeto__descricao__icontains=busca)
        )

    return qs.order_by('nome')


def equipe_detail(*, user: Usuario, pk) -> Equipe:
    """Obtém detalhes de uma equipe."""
    equipe = Equipe.objects.select_related(
        'projeto',
        'lider',
        'lider__pessoa_fisica',
        'coordenador',
        'coordenador__pessoa_fisica'
    ).prefetch_related(
        'membros',
        'membros__funcionario',
        'membros__funcionario__pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=equipe.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso a esta equipe.")

    return equipe


def equipes_por_projeto(*, user: Usuario, projeto_id: str) -> QuerySet:
    """Lista equipes de um projeto."""
    qs = Equipe.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related('lider__pessoa_fisica', 'coordenador__pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('nome')


def membros_equipe(*, user: Usuario, equipe_id: str, apenas_ativos: bool = True) -> QuerySet:
    """Lista membros de uma equipe."""
    qs = EquipeFuncionario.objects.filter(
        equipe_id=equipe_id,
        deleted_at__isnull=True
    ).select_related('funcionario', 'funcionario__pessoa_fisica', 'funcionario__cargo')

    if apenas_ativos:
        qs = qs.filter(data_saida__isnull=True)

    return qs.order_by('funcionario__pessoa_fisica__nome_completo')


# ============================================================================
# Alocação Selectors
# ============================================================================

def alocacao_list(
    *,
    user: Usuario,
    funcionario_id: str = None,
    projeto_id: str = None,
    apenas_ativas: bool = False
) -> QuerySet:
    """Lista alocações com filtros opcionais."""
    qs = Alocacao.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'projeto'
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    if apenas_ativas:
        qs = qs.filter(data_fim__isnull=True)

    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)

    if projeto_id:
        qs = qs.filter(projeto_id=projeto_id)

    return qs.order_by('-data_inicio')


def alocacao_detail(*, user: Usuario, pk) -> Alocacao:
    """Obtém detalhes de uma alocação."""
    alocacao = Alocacao.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__cargo',
        'projeto'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=alocacao.projeto.filial_id).exists():
            raise PermissionDenied("Usuário não tem acesso a esta alocação.")

    return alocacao


def alocacoes_por_funcionario(*, user: Usuario, funcionario_id: str) -> QuerySet:
    """Lista histórico de alocações de um funcionário."""
    qs = Alocacao.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).select_related('projeto')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_inicio')


def alocacoes_por_projeto(*, user: Usuario, projeto_id: str, apenas_ativas: bool = True) -> QuerySet:
    """Lista alocações de um projeto."""
    qs = Alocacao.objects.filter(
        projeto_id=projeto_id,
        deleted_at__isnull=True
    ).select_related('funcionario', 'funcionario__pessoa_fisica', 'funcionario__cargo')

    if apenas_ativas:
        qs = qs.filter(data_fim__isnull=True)

    return qs.order_by('funcionario__pessoa_fisica__nome_completo')
