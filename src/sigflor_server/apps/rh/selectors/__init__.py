# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas do modulo RH.
"""
from django.db.models import QuerySet, Q, Count
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied

from ..models import Cargo, Funcionario, Dependente
from apps.comum.models.usuarios import Usuario # Importando Usuario para type hinting


def funcionario_list(
    *,
    user: Usuario, # Adicionado parametro user
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
    """Lista funcionarios com filtros opcionais, respeitando permissoes regionais do usuario."""
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
        'subcontrato__contrato__contratante__pessoa_juridica',
        'projeto',
        'projeto__filial',
        'projeto__cliente__pessoa_juridica',
    )

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

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
        qs = qs.filter(projeto__filial_id=filial_id)

    if contrato_id:
        qs = qs.filter(projeto__cliente__contratos__id=contrato_id) # Via contrato do cliente do projeto

    if search:
        qs = qs.filter(
            Q(pessoa_fisica__nome_completo__icontains=search) |
            Q(pessoa_fisica__cpf__icontains=search) |
            Q(matricula__icontains=search) |
            Q(cargo__nome__icontains=search)
        )

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionario_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Funcionario:
    """Obtem detalhes de um funcionario com relacionamentos, verificando permissao regional."""
    funcionario = Funcionario.objects.select_related(
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
        'subcontrato__contrato__contratante__pessoa_juridica',
        'projeto',
        'projeto__filial',
        'projeto__cliente__pessoa_juridica',
    ).prefetch_related(
        'pessoa_fisica__enderecos',
        'pessoa_fisica__contatos',
        'pessoa_fisica__documentos',
        'subordinados',
        'subordinados__pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not funcionario.projeto or not user.allowed_filiais.filter(id=funcionario.projeto.filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso ao funcionário {funcionario.nome} via filial do projeto.")

    return funcionario


def funcionarios_por_departamento(*, user: Usuario, departamento: str) -> QuerySet:
    """Lista funcionarios de um departamento especifico, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        departamento__iexact=departamento,
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_empresa(*, user: Usuario, empresa_id: str) -> QuerySet:
    """Lista funcionarios de uma empresa especifica, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        empresa_id=empresa_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_subcontrato(*, user: Usuario, subcontrato_id: str) -> QuerySet:
    """Lista funcionarios de um subcontrato especifico, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        subcontrato_id=subcontrato_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_filial(*, user: Usuario, filial_id: str) -> QuerySet:
    """Lista funcionarios de uma filial especifica (via projeto), respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        projeto__filial_id=filial_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'subcontrato')

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=filial_id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial_id}.")

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_por_contrato(*, user: Usuario, contrato_id: str) -> QuerySet:
    """Lista funcionarios de um contrato especifico (via projeto), respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        projeto__cliente__contratos__id=contrato_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica', 'cargo', 'subcontrato')

    if not user.is_superuser:
        # Verifica se o usuário tem acesso às filiais associadas a este contrato através dos projetos.
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_ativos(*, user: Usuario) -> QuerySet:
    """Lista apenas funcionarios ativos, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_afastados(*, user: Usuario) -> QuerySet:
    """Lista funcionarios afastados (afastado, ferias, licenca), respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        status__in=[
            Funcionario.Status.AFASTADO,
            Funcionario.Status.FERIAS,
            Funcionario.Status.LICENCA
        ],
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_admitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionarios admitidos em um periodo, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        data_admissao__gte=data_inicio,
        data_admissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_admissao')


def funcionarios_demitidos_periodo(*, user: Usuario, data_inicio, data_fim) -> QuerySet:
    """Lista funcionarios demitidos em um periodo, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        data_demissao__gte=data_inicio,
        data_demissao__lte=data_fim,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('-data_demissao')


def aniversariantes_mes(*, user: Usuario, mes: int = None) -> QuerySet:
    """Lista funcionarios que fazem aniversario no mes, respeitando permissoes regionais do usuario."""
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
    """Lista subordinados diretos de um gestor, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        gestor_id=gestor_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_rh(*, user: Usuario) -> dict:
    """Retorna estatisticas gerais do RH, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

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
    user: Usuario, # Adicionado parametro user
    funcionario_id: str = None,
    search: str = None,
    parentesco: str = None,
    incluso_ir: bool = None,
    incluso_plano_saude: bool = None
) -> QuerySet:
    """Lista dependentes com filtros opcionais, respeitando permissoes regionais do usuario."""
    qs = Dependente.objects.filter(
        deleted_at__isnull=True
    ).select_related('funcionario', 'funcionario__pessoa_fisica')

    if not user.is_superuser:
        # Dependentes são vinculados a Funcionários, que por sua vez estão vinculados a Projetos/Filiais.
        # Filtra os dependentes cujos funcionários estão em filiais permitidas ao usuário.
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

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


def dependente_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Dependente:
    """Obtem detalhes de um dependente, verificando permissao regional."""
    dependente = Dependente.objects.select_related(
        'funcionario',
        'funcionario__pessoa_fisica',
        'funcionario__projeto__filial' # Adicionado para verificação de permissão
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not dependente.funcionario.projeto or not user.allowed_filiais.filter(id=dependente.funcionario.projeto.filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso ao dependente {dependente.nome_completo} via filial do funcionário.")

    return dependente


def dependentes_por_funcionario(*, user: Usuario, funcionario_id: str) -> QuerySet:
    """Lista dependentes de um funcionario especifico, respeitando permissoes regionais do usuario."""
    qs = Dependente.objects.filter(
        funcionario_id=funcionario_id,
        deleted_at__isnull=True
    ).select_related('funcionario__pessoa_fisica', 'funcionario__projeto__filial') # Adicionado para verificação de permissão

    if not user.is_superuser:
        # Verifica se o funcionário (pai do dependente) está em uma filial permitida.
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('nome_completo')


def funcionarios_com_dependentes(*, user: Usuario) -> QuerySet:
    """Lista funcionarios que possuem dependentes, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def funcionarios_sem_dependentes(*, user: Usuario) -> QuerySet:
    """Lista funcionarios que nao possuem dependentes, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        tem_dependente=False,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_dependentes(*, user: Usuario) -> dict:
    """Retorna estatisticas de dependentes, respeitando permissoes regionais do usuario."""
    qs = Dependente.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(funcionario__projeto__filial__in=user.allowed_filiais.all()).distinct()

    total = qs.count()
    incluso_ir = qs.filter(incluso_ir=True).count()
    incluso_plano = qs.filter(incluso_plano_saude=True).count()

    por_parentesco = qs.values('parentesco').annotate(
        total=Count('id')
    ).order_by('-total')

    funcionarios_com_dep = Funcionario.objects.filter(
        tem_dependente=True,
        deleted_at__isnull=True
    )
    if not user.is_superuser:
        funcionarios_com_dep = funcionarios_com_dep.filter(projeto__filial__in=user.allowed_filiais.all())
    funcionarios_com_dep = funcionarios_com_dep.count()

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
    user: Usuario, # Adicionado parametro user
    search: str = None,
    ativo: bool = None,
    cbo: str = None
) -> QuerySet:
    """Lista cargos com filtros opcionais. Nao ha restricao regional direta no cargo, mas a listagem pode ser relevante no contexto regional."""
    # Cargos nao tem uma filial direta, entao a permissao regional pode ser aplicada indiretamente
    # por exemplo, listando apenas cargos associados a funcionarios em filiais permitidas.
    # Para o MVP, vamos deixar a listagem de cargos global, mas se no futuro houver
    # uma ligacao direta de Cargo a Filial, a logica precisaria ser revista aqui.
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    # Apenas como exemplo de como se poderia filtrar, se cargos tivessem filial_id
    # if not user.is_superuser:
    #     qs = qs.filter(filial__in=user.allowed_filiais.all())

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


def cargo_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Cargo:
    """Obtem detalhes de um cargo. Nao ha restricao regional direta no cargo."""
    cargo = Cargo.objects.get(pk=pk, deleted_at__isnull=True)

    # Similar a cargo_list, nenhuma verificacao regional direta para o MVP.
    # if not user.is_superuser:
    #     # Exemplo: Se o cargo tivesse uma filial associada
    #     if not user.allowed_filiais.filter(id=cargo.filial.id).exists():
    #         raise PermissionDenied(f"Usuário não tem acesso ao cargo {cargo.nome} via filial.")

    return cargo


def cargos_ativos(*, user: Usuario) -> QuerySet:
    """Lista apenas cargos ativos. Nao ha restricao regional direta no cargo."""
    qs = Cargo.objects.filter(
        ativo=True,
        deleted_at__isnull=True
    ).order_by('nome')

    # if not user.is_superuser:
    #     qs = qs.filter(filial__in=user.allowed_filiais.all())

    return qs


def funcionarios_por_cargo(
    *,
    user: Usuario, # Adicionado parametro user
    cargo_id: str
) -> QuerySet:
    """Lista funcionarios de um cargo especifico, respeitando permissoes regionais do usuario."""
    qs = Funcionario.objects.filter(
        cargo_id=cargo_id,
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if not user.is_superuser:
        qs = qs.filter(projeto__filial__in=user.allowed_filiais.all()).distinct()

    return qs.order_by('pessoa_fisica__nome_completo')


def estatisticas_cargos(*, user: Usuario) -> dict:
    """Retorna estatisticas de cargos. A contagem de funcionarios respeita permissoes regionais."""
    qs = Cargo.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    ativos = qs.filter(ativo=True).count()

    funcionarios_qs = Funcionario.objects.filter(
        status=Funcionario.Status.ATIVO,
        deleted_at__isnull=True
    )
    if not user.is_superuser:
        funcionarios_qs = funcionarios_qs.filter(projeto__filial__in=user.allowed_filiais.all())

    por_cargo = funcionarios_qs.values('cargo__nome').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total_cargos': total,
        'cargos_ativos': ativos,
        'funcionarios_por_cargo': list(por_cargo),
    }