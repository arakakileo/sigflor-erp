from .base import TimeStampedModel, AuditModel, SoftDeleteModel
from .pessoa_fisica import PessoaFisica
from .pessoa_juridica import PessoaJuridica, SituacaoCadastral
from .empresas import Empresa
from .clientes import Cliente
from .filiais import Filial
from .enderecos import (
    Endereco, TipoEndereco,
    PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco
)
from .contatos import Contato, PessoaFisicaContato, PessoaJuridicaContato, FilialContato
from .documentos import Documento, PessoaFisicaDocumento, PessoaJuridicaDocumento
from .anexos import Anexo
from .deficiencias import Deficiencia, PessoaFisicaDeficiencia
from .projeto import Projeto, StatusProjeto

__all__ = [
    # Base
    'TimeStampedModel',
    'AuditModel',
    'SoftDeleteModel',
    # Pessoas
    'PessoaFisica',
    'PessoaJuridica',
    'SituacaoCadastral',
    # Empresas e Estrutura
    'Empresa',
    'Cliente',
    'Filial',
    'Projeto',
    'StatusProjeto',
    # Entidades genericas
    'Endereco',
    'TipoEndereco',
    'PessoaFisicaEndereco',
    'PessoaJuridicaEndereco',
    'FilialEndereco',
    'Contato',
    'PessoaFisicaContato',
    'PessoaJuridicaContato',
    'FilialContato',
    'Documento',
    'PessoaFisicaDocumento',
    'PessoaJuridicaDocumento',
    'Anexo',
    'Deficiencia',
    'PessoaFisicaDeficiencia',
]
