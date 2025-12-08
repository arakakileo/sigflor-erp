from .pessoa_fisica import PessoaFisicaSerializer
from .pessoa_juridica import (
    PessoaJuridicaSerializer,
    PessoaJuridicaCreateSerializer,
    PessoaJuridicaUpdateSerializer,
    PessoaJuridicaListSerializer
)
from .empresas import EmpresaListSerializer, EmpresaSerializer, EmpresaCreateSerializer
from .clientes import ClienteListSerializer, ClienteSerializer, ClienteCreateSerializer
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
    'EmpresaCreateSerializer',
    'EmpresaListSerializer',
    'EmpresaSerializer',
    'ClienteListSerializer',
    'ClienteSerializer',
    'ClienteCreateSerializer',
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
    # Projeto
    'ProjetoSerializer',
    'ProjetoListSerializer',
    'ProjetoCreateSerializer',
    'ProjetoUpdateSerializer',
    # Exame
    'ExameSerializer',
]
