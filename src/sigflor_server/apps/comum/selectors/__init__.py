# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas.
Centralizam queries complexas e evitam N+1 usando select_related e prefetch_related.
"""
from django.db.models import QuerySet, Q
from django.contrib.contenttypes.models import ContentType

from ..models import (
    PessoaFisica, PessoaJuridica, Usuario, Permissao, Papel,
    EmpresaCNPJ, Contratante, Endereco, Contato, Documento, Anexo, Deficiencia,
    Filial, Contrato, SubContrato
)


# ============ Pessoa Fisica ============

def pessoa_fisica_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista pessoas fisicas com filtros opcionais."""
    qs = PessoaFisica.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome_completo__icontains=search) |
            Q(cpf__icontains=search)
        )

    return qs.order_by('nome_completo')


def pessoa_fisica_detail(*, pk) -> PessoaFisica:
    """Obtem detalhes de uma pessoa fisica com relacionamentos."""
    return PessoaFisica.objects.prefetch_related(
        'enderecos', 'contatos', 'documentos', 'anexos'
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Pessoa Juridica ============

def pessoa_juridica_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista pessoas juridicas com filtros opcionais."""
    qs = PessoaJuridica.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(razao_social__icontains=search) |
            Q(nome_fantasia__icontains=search) |
            Q(cnpj__icontains=search)
        )

    return qs.order_by('razao_social')


def pessoa_juridica_detail(*, pk) -> PessoaJuridica:
    """Obtem detalhes de uma pessoa juridica com relacionamentos."""
    return PessoaJuridica.objects.prefetch_related(
        'enderecos', 'contatos', 'documentos', 'anexos'
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Usuario ============

def usuario_list(*, filters: dict = None, search: str = None, ativo: bool = None) -> QuerySet:
    """Lista usuarios com filtros opcionais."""
    qs = Usuario.objects.filter(deleted_at__isnull=True)

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    return qs.select_related('pessoa_fisica').prefetch_related('papeis').order_by('username')


def usuario_detail(*, pk) -> Usuario:
    """Obtem detalhes de um usuario com relacionamentos."""
    return Usuario.objects.select_related(
        'pessoa_fisica'
    ).prefetch_related(
        'papeis', 'papeis__permissoes', 'permissoes_diretas'
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Permissao e Papel ============

def permissao_list(*, search: str = None) -> QuerySet:
    """Lista permissoes."""
    qs = Permissao.objects.filter(deleted_at__isnull=True)

    if search:
        qs = qs.filter(
            Q(codigo__icontains=search) |
            Q(nome__icontains=search)
        )

    return qs.order_by('codigo')


def papel_list(*, search: str = None) -> QuerySet:
    """Lista papeis com permissoes."""
    qs = Papel.objects.filter(deleted_at__isnull=True).prefetch_related('permissoes')

    if search:
        qs = qs.filter(Q(nome__icontains=search))

    return qs.order_by('nome')


def papel_detail(*, pk) -> Papel:
    """Obtem detalhes de um papel com permissoes."""
    return Papel.objects.prefetch_related('permissoes').get(pk=pk, deleted_at__isnull=True)


# ============ Empresa CNPJ ============

def empresa_cnpj_list(*, filters: dict = None, search: str = None, ativa: bool = None) -> QuerySet:
    """Lista empresas do grupo com filtros opcionais."""
    qs = EmpresaCNPJ.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica')

    if ativa is not None:
        qs = qs.filter(ativa=ativa)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(pessoa_juridica__razao_social__icontains=search) |
            Q(pessoa_juridica__cnpj__icontains=search)
        )

    return qs.order_by('pessoa_juridica__razao_social')


def empresa_cnpj_detail(*, pk) -> EmpresaCNPJ:
    """Obtem detalhes de uma empresa com relacionamentos."""
    return EmpresaCNPJ.objects.select_related(
        'pessoa_juridica'
    ).prefetch_related(
        'pessoa_juridica__enderecos',
        'pessoa_juridica__contatos',
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Contratante ============

def contratante_list(*, filters: dict = None, search: str = None, ativo: bool = None) -> QuerySet:
    """Lista contratantes com filtros opcionais."""
    qs = Contratante.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica')

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(pessoa_juridica__razao_social__icontains=search) |
            Q(pessoa_juridica__nome_fantasia__icontains=search) |
            Q(pessoa_juridica__cnpj__icontains=search)
        )

    return qs.order_by('pessoa_juridica__razao_social')


def contratante_detail(*, pk) -> Contratante:
    """Obtem detalhes de um contratante com relacionamentos."""
    return Contratante.objects.select_related(
        'pessoa_juridica'
    ).prefetch_related(
        'pessoa_juridica__enderecos',
        'pessoa_juridica__contatos',
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Endereco ============

def endereco_list_por_entidade(*, entidade, principal: bool = None) -> QuerySet:
    """Lista enderecos de uma entidade."""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Endereco.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if principal is not None:
        qs = qs.filter(principal=principal)

    return qs.order_by('-principal', '-created_at')


# ============ Contato ============

def contato_list_por_entidade(*, entidade, tipo: str = None) -> QuerySet:
    """Lista contatos de uma entidade."""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Contato.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if tipo:
        qs = qs.filter(tipo=tipo)

    return qs.order_by('tipo', '-principal', '-created_at')


# ============ Documento ============

def documento_list_por_entidade(*, entidade, tipo: str = None, vencidos: bool = None) -> QuerySet:
    """Lista documentos de uma entidade."""
    from django.utils import timezone

    content_type = ContentType.objects.get_for_model(entidade)
    qs = Documento.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if tipo:
        qs = qs.filter(tipo=tipo)

    if vencidos is True:
        qs = qs.filter(data_validade__lt=timezone.now().date())
    elif vencidos is False:
        qs = qs.filter(
            Q(data_validade__isnull=True) |
            Q(data_validade__gte=timezone.now().date())
        )

    return qs.order_by('tipo', '-principal', '-created_at')


# ============ Anexo ============

def anexo_list_por_entidade(*, entidade, mimetype: str = None) -> QuerySet:
    """Lista anexos de uma entidade."""
    content_type = ContentType.objects.get_for_model(entidade)
    qs = Anexo.objects.filter(
        content_type=content_type,
        object_id=str(entidade.pk),
        deleted_at__isnull=True
    )

    if mimetype:
        qs = qs.filter(mimetype__startswith=mimetype)

    return qs.order_by('-created_at')


# ============ Deficiencia ============

def deficiencia_list(
    *,
    pessoa_fisica_id: str = None,
    search: str = None,
    tipo: str = None,
    cid: str = None
) -> QuerySet:
    """Lista deficiencias com filtros opcionais."""
    qs = Deficiencia.objects.filter(
        deleted_at__isnull=True
    ).select_related('pessoa_fisica')

    if pessoa_fisica_id:
        qs = qs.filter(pessoa_fisica_id=pessoa_fisica_id)

    if tipo:
        qs = qs.filter(tipo=tipo)

    if cid:
        qs = qs.filter(cid__icontains=cid)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(cid__icontains=search) |
            Q(pessoa_fisica__nome_completo__icontains=search)
        )

    return qs.order_by('pessoa_fisica__nome_completo', 'nome')


def deficiencia_detail(*, pk) -> Deficiencia:
    """Obtem detalhes de uma deficiencia."""
    return Deficiencia.objects.select_related(
        'pessoa_fisica'
    ).get(pk=pk, deleted_at__isnull=True)


def deficiencias_por_pessoa(*, pessoa_fisica_id: str) -> QuerySet:
    """Lista deficiencias de uma pessoa fisica especifica."""
    return Deficiencia.objects.filter(
        pessoa_fisica_id=pessoa_fisica_id,
        deleted_at__isnull=True
    ).order_by('nome')


def pessoas_com_deficiencia() -> QuerySet:
    """Lista pessoas fisicas que possuem deficiencias."""
    return PessoaFisica.objects.filter(
        possui_deficiencia=True,
        deleted_at__isnull=True
    ).order_by('nome_completo')


def estatisticas_deficiencias() -> dict:
    """Retorna estatisticas de deficiencias."""
    from django.db.models import Count

    qs = Deficiencia.objects.filter(deleted_at__isnull=True)

    total = qs.count()
    congenitas = qs.filter(congenita=True).count()

    por_tipo = qs.values('tipo').annotate(
        total=Count('id')
    ).order_by('-total')

    pessoas_com_def = PessoaFisica.objects.filter(
        possui_deficiencia=True,
        deleted_at__isnull=True
    ).count()

    return {
        'total_deficiencias': total,
        'congenitas': congenitas,
        'adquiridas': total - congenitas,
        'por_tipo': list(por_tipo),
        'pessoas_com_deficiencia': pessoas_com_def,
    }


# ============ Filial ============

def filial_list(
    *,
    filters: dict = None,
    search: str = None,
    status: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista filiais com filtros opcionais."""
    qs = Filial.objects.filter(deleted_at__isnull=True).select_related('empresa')

    if status:
        qs = qs.filter(status=status)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search) |
            Q(codigo_interno__icontains=search)
        )

    return qs.order_by('nome')


def filial_detail(*, pk) -> Filial:
    """Obtem detalhes de uma filial com relacionamentos."""
    return Filial.objects.select_related(
        'empresa', 'empresa__pessoa_juridica'
    ).prefetch_related(
        'enderecos', 'contatos', 'subcontratos'
    ).get(pk=pk, deleted_at__isnull=True)


def filiais_ativas(*, empresa_id: str = None) -> QuerySet:
    """Lista filiais ativas."""
    qs = Filial.objects.filter(
        status=Filial.Status.ATIVA,
        deleted_at__isnull=True
    ).select_related('empresa')

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('nome')


def estatisticas_filiais() -> dict:
    """Retorna estatisticas de filiais."""
    from django.db.models import Count

    qs = Filial.objects.filter(deleted_at__isnull=True)

    total = qs.count()

    por_status = qs.values('status').annotate(
        total=Count('id')
    ).order_by('-total')

    return {
        'total': total,
        'por_status': list(por_status),
    }


# ============ Contrato ============

def contrato_list(
    *,
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    vigente: bool = None,
    contratante_id: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista contratos com filtros opcionais."""
    from django.utils import timezone

    qs = Contrato.objects.filter(
        deleted_at__isnull=True
    ).select_related('contratante', 'empresa', 'contratante__pessoa_juridica', 'empresa__pessoa_juridica')

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if vigente is True:
        hoje = timezone.now().date()
        qs = qs.filter(
            ativo=True,
            data_inicio__lte=hoje
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
        )
    elif vigente is False:
        hoje = timezone.now().date()
        qs = qs.filter(
            Q(ativo=False) |
            Q(data_inicio__gt=hoje) |
            Q(data_fim__lt=hoje)
        )

    if contratante_id:
        qs = qs.filter(contratante_id=contratante_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(numero_interno__icontains=search) |
            Q(numero_externo__icontains=search) |
            Q(contratante__pessoa_juridica__razao_social__icontains=search)
        )

    return qs.order_by('-data_inicio', 'numero_interno')


def contrato_detail(*, pk) -> Contrato:
    """Obtem detalhes de um contrato com relacionamentos."""
    return Contrato.objects.select_related(
        'contratante', 'empresa',
        'contratante__pessoa_juridica', 'empresa__pessoa_juridica'
    ).prefetch_related(
        'subcontratos'
    ).get(pk=pk, deleted_at__isnull=True)


def contratos_vigentes(*, contratante_id: str = None, empresa_id: str = None) -> QuerySet:
    """Lista contratos vigentes."""
    from django.utils import timezone

    hoje = timezone.now().date()
    qs = Contrato.objects.filter(
        ativo=True,
        data_inicio__lte=hoje,
        deleted_at__isnull=True
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).select_related('contratante', 'empresa')

    if contratante_id:
        qs = qs.filter(contratante_id=contratante_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('-data_inicio', 'numero_interno')


def estatisticas_contratos() -> dict:
    """Retorna estatisticas de contratos."""
    from django.db.models import Count, Sum
    from django.utils import timezone

    qs = Contrato.objects.filter(deleted_at__isnull=True)
    hoje = timezone.now().date()

    total = qs.count()
    ativos = qs.filter(ativo=True).count()
    vigentes = qs.filter(
        ativo=True,
        data_inicio__lte=hoje
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).count()

    valor_total = qs.filter(ativo=True).aggregate(
        total=Sum('valor')
    )['total'] or 0

    return {
        'total': total,
        'ativos': ativos,
        'inativos': total - ativos,
        'vigentes': vigentes,
        'valor_total': valor_total,
    }


# ============ SubContrato ============

def subcontrato_list(
    *,
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    vigente: bool = None,
    filial_id: str = None,
    contrato_id: str = None
) -> QuerySet:
    """Lista subcontratos com filtros opcionais."""
    from django.utils import timezone

    qs = SubContrato.objects.filter(
        deleted_at__isnull=True
    ).select_related(
        'filial', 'contrato',
        'contrato__contratante', 'contrato__empresa',
        'contrato__contratante__pessoa_juridica', 'contrato__empresa__pessoa_juridica'
    )

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if vigente is True:
        hoje = timezone.now().date()
        qs = qs.filter(
            ativo=True,
            data_inicio__lte=hoje
        ).filter(
            Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
        )
    elif vigente is False:
        hoje = timezone.now().date()
        qs = qs.filter(
            Q(ativo=False) |
            Q(data_inicio__gt=hoje) |
            Q(data_fim__lt=hoje)
        )

    if filial_id:
        qs = qs.filter(filial_id=filial_id)

    if contrato_id:
        qs = qs.filter(contrato_id=contrato_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(numero__icontains=search) |
            Q(filial__nome__icontains=search) |
            Q(contrato__numero_interno__icontains=search)
        )

    return qs.order_by('-data_inicio', 'numero')


def subcontrato_detail(*, pk) -> SubContrato:
    """Obtem detalhes de um subcontrato com relacionamentos."""
    return SubContrato.objects.select_related(
        'filial', 'contrato',
        'contrato__contratante', 'contrato__empresa',
        'contrato__contratante__pessoa_juridica', 'contrato__empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)


def subcontratos_vigentes(*, filial_id: str = None, contrato_id: str = None) -> QuerySet:
    """Lista subcontratos vigentes."""
    from django.utils import timezone

    hoje = timezone.now().date()
    qs = SubContrato.objects.filter(
        ativo=True,
        data_inicio__lte=hoje,
        deleted_at__isnull=True
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).select_related('filial', 'contrato')

    if filial_id:
        qs = qs.filter(filial_id=filial_id)

    if contrato_id:
        qs = qs.filter(contrato_id=contrato_id)

    return qs.order_by('-data_inicio', 'numero')


def subcontratos_por_filial(*, filial_id: str) -> QuerySet:
    """Lista subcontratos de uma filial especifica."""
    return SubContrato.objects.filter(
        filial_id=filial_id,
        deleted_at__isnull=True
    ).select_related('contrato').order_by('-data_inicio', 'numero')


def subcontratos_por_contrato(*, contrato_id: str) -> QuerySet:
    """Lista subcontratos de um contrato especifico."""
    return SubContrato.objects.filter(
        contrato_id=contrato_id,
        deleted_at__isnull=True
    ).select_related('filial').order_by('-data_inicio', 'numero')


def estatisticas_subcontratos() -> dict:
    """Retorna estatisticas de subcontratos."""
    from django.db.models import Count
    from django.utils import timezone

    qs = SubContrato.objects.filter(deleted_at__isnull=True)
    hoje = timezone.now().date()

    total = qs.count()
    ativos = qs.filter(ativo=True).count()
    vigentes = qs.filter(
        ativo=True,
        data_inicio__lte=hoje
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).count()

    por_filial = qs.values('filial__nome').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    return {
        'total': total,
        'ativos': ativos,
        'inativos': total - ativos,
        'vigentes': vigentes,
        'por_filial': list(por_filial),
    }
