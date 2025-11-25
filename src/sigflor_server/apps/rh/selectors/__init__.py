# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas do modulo RH.
"""
from django.db.models import QuerySet, Q, Count
from django.utils import timezone

from ..models import Cargo, Funcionario, Dependente


def funcionario_list(
    *,
    search: str = None,
    status: str = None,
    departamento: str = None,
    tipo_contrato: str = None,
    empresa_id: str = None,
    gestor_id: str = None,
    cargo_id: str = None,
    subcontrato_id: str = None,
    filial_id: str = None,
    contrato_id: str = None,
    apenas_ativos: bool = False
) -> QuerySet:
    """Lista funcionarios com filtros opcionais."""
    qs = Funcionario.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'gestor',
        'gestor__pessoa_fisica',
        'subcontrato',
        'subcontrato__filial',
        'subcontrato__contrato',
        'subcontrato__contrato__contratante',
        'subcontrato__contrato__contratante__pessoa_juridica'
    )

    if apenas_ativos:
        qs = qs.filter(status=Funcionario.Status.ATIVO)

    if status:
        qs = qs.filter(status=status)

    if departamento:
        qs = qs.filter(departamento__icontains=departamento)

    if tipo_contrato:
        qs = qs.filter(tipo_contrato=tipo_contrato)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if gestor_id:
        qs = qs.filter(gestor_id=gestor_id)

    if cargo_id:
        qs = qs.filter(cargo_id=cargo_id)

    if subcontrato_id:
        qs = qs.filter(subcontrato_id=subcontrato_id)

    if filial_id:
        qs = qs.filter(subcontrato__filial_id=filial_id)

    if contrato_id:
        qs = qs.filter(subcontrato__contrato_id=contrato_id)

    if search:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=search) |
            Q(pessoa_fisica__cpf__icontains=search) |
            Q(matricula__icontains=search) |
            Q(cargo__nome__icontains=search)
        )

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionario_detail(*, pk) -> Funcionario:
    """Obtem detalhes de um funcionario com relacionamentos."""
    return Funcionario.objects.select_related(
        'pessoa_fisica',
        'cargo',
        'empresa',
        'empresa__pessoa_juridica',
        'gestor',
        'gestor__pessoa_fisica',
        'subcontrato',
        'subcontrato__filial',
        'subcontrato__contrato',
        'subcontrato__contrato__contratante',
        'subcontrato__contrato__contratante__pessoa_juridica'
    ).prefetch_related(
        'pessoa_fisica__enderecos',
        'pessoa_fisica__contatos',
        'pessoa_fisica__documentos',
        'subordinados',
        'subordinados__pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)


def funcionarios_por_departamento(*, departamento: str) -> QuerySet:
    """Lista funcionarios de um departamento especifico."""
    return Funcionario.objects.filter(
        departamento__iexact=departamento,
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def funcionarios_por_empresa(*, empresa_id: str) -> QuerySet:
    """Lista funcionarios de uma empresa especifica."""
    return Funcionario.objects.filter(
        empresa_id=empresa_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def funcionarios_por_subcontrato(*, subcontrato_id: str) -> QuerySet:
    """Lista funcionarios de um subcontrato especifico."""
    return Funcionario.objects.filter(
        subcontrato_id=subcontrato_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo').order_by('pessoa_fisica__nome_completo')


def funcionarios_por_filial(*, filial_id: str) -> QuerySet:
    """Lista funcionarios de uma filial especifica (via subcontrato)."""
    return Funcionario.objects.filter(
        subcontrato__filial_id=filial_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'subcontrato').order_by('pessoa_fisica__nome_completo')


def funcionarios_por_contrato(*, contrato_id: str) -> QuerySet:
    """Lista funcionarios de um contrato especifico (via subcontrato)."""
    return Funcionario.objects.filter(
        subcontrato__contrato_id=contrato_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'subcontrato').order_by('pessoa_fisica__nome_completo')


def funcionarios_ativos() -> QuerySet:
    """Lista apenas funcionarios ativos."""
    return Funcionario.objects.filter(
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def funcionarios_afastados() -> QuerySet:
    """Lista funcionarios afastados (afastado, ferias, licenca)."""
    return Funcionario.objects.filter(
        status__in=[
            Funcionario.Status.AFASTADO,
            Funcionario.Status.FERIAS,
            Funcionario.Status.LICENCA
        ],
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def funcionarios_admitidos_periodo(*, data_inicio, data_fim) -> QuerySet:
    """Lista funcionarios admitidos em um periodo."""
    return Funcionario.objects.filter(
        data_admissao__gte=data_inicio,
        data_admissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('-data_admissao')


def funcionarios_demitidos_periodo(*, data_inicio, data_fim) -> QuerySet:
    """Lista funcionarios demitidos em um periodo."""
    return Funcionario.objects.filter(
        data_demissao__gte=data_inicio,
        data_demissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('-data_demissao')


def aniversariantes_mes(*, mes: int = None) -> QuerySet:
    """Lista funcionarios que fazem aniversario no mes."""
    if mes is None:
        mes = timezone.now().month

    return Funcionario.objects.filter(
        pessoa_fisica__data_nascimento__month=mes,
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__data_nascimento__day')


def subordinados_diretos(*, gestor_id: str) -> QuerySet:
    """Lista subordinados diretos de um gestor."""
    return Funcionario.objects.filter(
        gestor_id=gestor_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def estatisticas_rh() -> dict:
    """Retorna estatisticas gerais do RH."""
    qs = Funcionario.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    ativos = qs.filter(status=Funcionario.Status.ATIVO).count()
    afastados = qs.filter(status__in=[
        Funcionario.Status.AFASTADO,
        Funcionario.Status.FERIAS,
        Funcionario.Status.LICENCA
    ]).count()

    por_departamento = qs.filter(
        status=Funcionario.Status.ATIVO
    ).values('departamento').annotate(
        total=Count('id')
    ).order_by('-total')

    por_tipo_contrato = qs.filter(
        status=Funcionario.Status.ATIVO
    ).values('tipo_contrato').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total': total,
        'ativos': ativos,
        'afastados': afastados,
        'por_departamento': list(por_departamento),
        'por_tipo_contrato': list(por_tipo_contrato),
    }


# ============ Dependentes ============

def dependente_list(
    *,
    funcionario_id: str = None,
    search: str = None,
    parentesco: str = None,
    incluso_ir: bool = None,
    incluso_plano_saude: bool = None
) -> QuerySet:
    """Lista dependentes com filtros opcionais."""
    qs = Dependente.objects.filter(
        deleted_at__isnull=True
    ).select_related('funcionario', 'funcionario__pessoa_fisica')

    if funcionario_id:
        qs = qs.filter(funcionario_id=funcionario_id)

    if parentesco:
        qs = qs.filter(parentesco=parentesco)

    if incluso_ir is not None:
        qs = qs.filter(incluso_ir=incluso_ir)

    if incluso_plano_saude is not None:
        qs = qs.filter(incluso_plano_saude=incluso_plano_saude)

    if search:
        qs = qs.filter(
            Q(nome_completo__icontains=search) |
            Q(cpf__icontains=search)
        )

    return qs.order_by('funcionario__pessoa_fisica__nome_completo', 'nome_completo')


def dependente_detail(*, pk) -> Dependente:
    """Obtem detalhes de um dependente."""
    return Dependente.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)


def dependentes_por_funcionario(*, funcionario_id: str) -> QuerySet:
    """Lista dependentes de um funcionario especifico."""
    return Dependente.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).order_by('nome_completo')


def funcionarios_com_dependentes() -> QuerySet:
    """Lista funcionarios que possuem dependentes."""
    return Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def funcionarios_sem_dependentes() -> QuerySet:
    """Lista funcionarios que nao possuem dependentes."""
    return Funcionario.objects.filter(
        tem_dependente=False,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def estatisticas_dependentes() -> dict:
    """Retorna estatisticas de dependentes."""
    qs = Dependente.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    incluso_ir = qs.filter(incluso_ir=True).count()
    incluso_plano = qs.filter(incluso_plano_saude=True).count()

    por_parentesco = qs.values('parentesco').annotate(
        total=Count('id')
    ).order_by('-total')

    funcionarios_com_dep = Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    ).count()

    return {
        'total_dependentes': total,
        'incluso_ir': incluso_ir,
        'incluso_plano_saude': incluso_plano,
        'por_parentesco': list(por_parentesco),
        'funcionarios_com_dependentes': funcionarios_com_dep,
    }


# ============ Cargos ============

def cargo_list(
    *,
    search: str = None,
    ativo: bool = None,
    cbo: str = None
) -> QuerySet:
    """Lista cargos com filtros opcionais."""
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if cbo:
        qs = qs.filter(cbo__icontains=cbo)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(cbo__icontains=search) |
            Q(descricao__icontains=search)
        )

    return qs.order_by('nome')


def cargo_detail(*, pk) -> Cargo:
    """Obtem detalhes de um cargo."""
    return Cargo.objects.get(pk=pk, deleted_at__isnull=True)


def cargos_ativos() -> QuerySet:
    """Lista apenas cargos ativos."""
    return Cargo.objects.filter(
        ativo=True,
        deleted_at__isnull=True
    ).order_by('nome')


def funcionarios_por_cargo(*, cargo_id: str) -> QuerySet:
    """Lista funcionarios de um cargo especifico."""
    return Funcionario.objects.filter(
        cargo_id=cargo_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica').order_by('pessoa_fisica__nome_completo')


def estatisticas_cargos() -> dict:
    """Retorna estatisticas de cargos."""
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    ativos = qs.filter(ativo=True).count()

    por_cargo = Funcionario.objects.filter(
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).values('cargo__nome').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total_cargos': total,
        'cargos_ativos': ativos,
        'funcionarios_por_cargo': list(por_cargo),
    }
