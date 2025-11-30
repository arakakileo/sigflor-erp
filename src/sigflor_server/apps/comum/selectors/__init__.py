# -*- coding: utf-8 -*-
"""
Selectors para consultas otimizadas.
Centralizam queries complexas e evitam N+1 usando select_related e prefetch_related.
"""
from django.db.models import QuerySet, Q
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import PermissionDenied

from ..models import (
    PessoaFisica, PessoaJuridica, Usuario, Permissao, Papel,
    Empresa, Cliente, Endereco, Contato, Documento, Anexo, Deficiencia,
    Filial, Contrato, Projeto, Exame
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

def empresa_list(*, filters: dict = None, search: str = None, ativa: bool = None) -> QuerySet:
    """Lista empresas do grupo com filtros opcionais."""
    qs = Empresa.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica')

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


def empresa_detail(*, pk) -> Empresa:
    """Obtem detalhes de uma empresa com relacionamentos."""
    return Empresa.objects.select_related(
        'pessoa_juridica'
    ).prefetch_related(
        'pessoa_juridica__enderecos',
        'pessoa_juridica__contatos',
    ).get(pk=pk, deleted_at__isnull=True)


# ============ Cliente ============

def cliente_list(
    *,
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    empresa_id: str = None # Adicionado para filtrar clientes por empresa gestora
) -> QuerySet:
    """Lista clientes com filtros opcionais."""
    qs = Cliente.objects.filter(deleted_at__isnull=True).select_related('pessoa_juridica', 'empresa_gestora')

    if ativo is not None:
        qs = qs.filter(ativo=ativo)

    if empresa_id:
        qs = qs.filter(empresa_gestora_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(pessoa_juridica__razao_social__icontains=search) |
            Q(pessoa_juridica__nome_fantasia__icontains=search) |
            Q(pessoa_juridica__cnpj__icontains=search)
        )

    return qs.order_by('pessoa_juridica__razao_social')


def cliente_detail(*, pk) -> Cliente:
    """Obtem detalhes de um cliente com relacionamentos."""
    return Cliente.objects.select_related(
        'pessoa_juridica', 'empresa_gestora'
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
    user: Usuario, # Adicionado parametro user
    filters: dict = None,
    search: str = None,
    status: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista filiais com filtros opcionais, respeitando permissoes regionais do usuario."""
    qs = Filial.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all()) # Filtra por filiais permitidas ao usuario

    qs = qs.select_related('empresa')

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


def filial_detail(*, user: Usuario, pk) -> Filial:
    """Obtem detalhes de uma filial com relacionamentos, verificando permissao regional."""
    filial = Filial.objects.select_related(
        'empresa', 'empresa__pessoa_juridica'
    ).prefetch_related(
        'enderecos', 'contatos'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id=filial.id).exists():
            raise PermissionDenied(f"Usuário não tem acesso à filial {filial.nome}.")
    
    return filial


def filiais_ativas(*, user: Usuario, empresa_id: str = None) -> QuerySet:
    """Lista filiais ativas, respeitando permissoes regionais do usuario."""
    qs = Filial.objects.filter(
        status=Filial.Status.ATIVA,
        deleted_at__isnull=True
    )
    
    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all())

    qs = qs.select_related('empresa')

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('nome')


def estatisticas_filiais(*, user: Usuario) -> dict:
    """Retorna estatisticas de filiais, respeitando permissoes regionais do usuario."""
    from django.db.models import Count

    qs = Filial.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(id__in=user.allowed_filiais.all())

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
    user: Usuario, # Adicionado parametro user
    filters: dict = None,
    search: str = None,
    ativo: bool = None,
    vigente: bool = None,
    cliente_id: str = None,
    empresa_id: str = None
) -> QuerySet:
    """Lista contratos com filtros opcionais, respeitando permissoes regionais do usuario."""
    from django.utils import timezone

    qs = Contrato.objects.filter(
        deleted_at__isnull=True
    ).select_related('cliente', 'empresa', 'cliente__pessoa_juridica', 'empresa__pessoa_juridica')

    if not user.is_superuser:
        # Contratos são associados a Empresas e Clientes, que podem estar em Filiais.
        # Para o MVP, assumimos que a permissão é pela filial associada à empresa do contrato
        # ou que o contrato em si não tem restrição regional direta, mas é acessível se as filiais do usuário
        # estão em alguma Empresa que gerencia o cliente do contrato.
        # Esta é uma lógica que pode ser refinada, mas para o MVP, vamos considerar a empresa do contrato.
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

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

    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(numero_interno__icontains=search) |
            Q(numero_externo__icontains=search) |
            Q(cliente__pessoa_juridica__razao_social__icontains=search)
        )

    return qs.order_by('-data_inicio', 'numero_interno')


def contrato_detail(
    *,
    user: Usuario, # Adicionado parametro user
    pk
) -> Contrato:
    """Obtem detalhes de um contrato com relacionamentos, verificando permissao regional."""
    contrato = Contrato.objects.select_related(
        'cliente', 'empresa',
        'cliente__pessoa_juridica', 'empresa__pessoa_juridica'
    ).get(pk=pk, deleted_at__isnull=True)

    if not user.is_superuser:
        if not user.allowed_filiais.filter(id__in=contrato.empresa.filiais.all()).exists():
             raise PermissionDenied(f"Usuário não tem acesso ao contrato {contrato.numero_interno} via filial.")

    return contrato


def contratos_vigentes(
    *,
    user: Usuario, # Adicionado parametro user
    cliente_id: str = None, empresa_id: str = None
) -> QuerySet:
    """Lista contratos vigentes, respeitando permissoes regionais do usuario."""
    from django.utils import timezone

    hoje = timezone.now().date()
    qs = Contrato.objects.filter(
        ativo=True,
        data_inicio__lte=hoje,
        deleted_at__isnull=True
    ).filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=hoje)
    ).select_related('cliente', 'empresa')

    if not user.is_superuser:
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

    if cliente_id:
        qs = qs.filter(cliente_id=cliente_id)

    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)

    return qs.order_by('-data_inicio', 'numero_interno')


def estatisticas_contratos(*, user: Usuario) -> dict:
    """Retorna estatisticas de contratos, respeitando permissoes regionais do usuario."""
    from django.db.models import Count, Sum
    from django.utils import timezone

    qs = Contrato.objects.filter(deleted_at__isnull=True)

    if not user.is_superuser:
        qs = qs.filter(empresa__filiais__in=user.allowed_filiais.all()).distinct()

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


# ============ Projeto ============

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


# ============ Exame ============

def exame_list(*, filters: dict = None, search: str = None) -> QuerySet:
    """Lista exames com filtros opcionais."""
    qs = Exame.objects.filter(deleted_at__isnull=True)

    if filters:
        qs = qs.filter(**filters)

    if search:
        qs = qs.filter(
            Q(nome__icontains=search)
        )

    return qs.order_by('nome')


def exame_detail(*, pk) -> Exame:
    """Obtem detalhes de um exame."""
    return Exame.objects.get(pk=pk, deleted_at__isnull=True)
