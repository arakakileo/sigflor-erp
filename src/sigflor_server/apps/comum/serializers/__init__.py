from .pessoa_fisica import PessoaFisicaSerializer
from .pessoa_juridica import (
    PessoaJuridicaSerializer,
    PessoaJuridicaCreateSerializer,
    PessoaJuridicaUpdateSerializer,
    PessoaJuridicaListSerializer
)
from .usuarios import UsuarioSerializer, UsuarioCreateSerializer
from .permissoes import PermissaoSerializer, PapelSerializer
from .empresas_cnpj import EmpresaCNPJSerializer, EmpresaCNPJCreateSerializer, EmpresaCNPJListSerializer
from .contratantes import ContratanteSerializer, ContratanteCreateSerializer, ContratanteListSerializer
from .enderecos import EnderecoSerializer
from .contatos import ContatoSerializer
from .documentos import DocumentoSerializer
from .anexos import AnexoSerializer
from .deficiencias import (
    DeficienciaSerializer,
    DeficienciaCreateSerializer,
    DeficienciaListSerializer
)
from .filiais import (
    FilialSerializer,
    FilialCreateSerializer,
    FilialListSerializer
)
from .contratos import (
    ContratoSerializer,
    ContratoCreateSerializer,
    ContratoListSerializer
)
from .projeto import (
    ProjetoSerializer,
    ProjetoListSerializer,
    ProjetoCreateSerializer,
    ProjetoUpdateSerializer
)
from .exame import ExameSerializer

__all__ = [
    'PessoaFisicaSerializer',
    'PessoaJuridicaSerializer',
    'PessoaJuridicaCreateSerializer',
    'PessoaJuridicaUpdateSerializer',
    'PessoaJuridicaListSerializer',
    'UsuarioSerializer',
    'UsuarioCreateSerializer',
    'PermissaoSerializer',
    'PapelSerializer',
    'EmpresaCNPJListSerializer',
    'EmpresaCNPJSerializer',
    'EmpresaCNPJCreateSerializer',
    'ContratanteListSerializer',
    'ContratanteSerializer',
    'ContratanteCreateSerializer',
    'EnderecoSerializer',
    'ContatoSerializer',
    'DocumentoSerializer',
    'AnexoSerializer',
    'DeficienciaSerializer',
    'DeficienciaCreateSerializer',
    'DeficienciaListSerializer',
    # Filiais
    'FilialSerializer',
    'FilialCreateSerializer',
    'FilialListSerializer',
    # Contratos
    'ContratoSerializer',
    'ContratoCreateSerializer',
    'ContratoListSerializer',
    # Projeto
    'ProjetoSerializer',
    'ProjetoListSerializer',
    'ProjetoCreateSerializer',
    'ProjetoUpdateSerializer',
    # Exame
    'ExameSerializer',
]
