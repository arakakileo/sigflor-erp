from django.db import models


class NivelCargo(models.TextChoices):
    OPERACIONAL = 'OPERACIONAL', 'Operacional'
    TECNICO = 'TECNICO', 'Técnico'
    SUPERVISAO = 'SUPERVISAO', 'Supervisão'
    COORDENACAO = 'COORDENACAO', 'Coordenação'
    GERENCIA = 'GERENCIA', 'Gerência'
    DIRETORIA = 'DIRETORIA', 'Diretoria'


class RiscoPadrao:
    FISICO = 'Ausência de risco físico'
    BIOLOGICO = 'Ausência de risco biológico'
    QUIMICO = 'Ausência de risco químico'
    ERGONOMICO = 'Ausência de risco ergonômico'
    ACIDENTE = 'Ausência de risco de acidente'


class Parentesco(models.TextChoices):
    FILHO = 'FILHO', 'Filho(a)'
    CONJUGE = 'CONJUGE', 'Cônjuge'
    IRMAO = 'IRMAO', 'Irmão(ã)'
    PAIS = 'PAIS', 'Pais'
    OUTROS = 'OUTROS', 'Outros'


class TipoEquipe(models.TextChoices):
    MANUAL = 'MANUAL', 'Manual'
    MECANIZADA = 'MECANIZADA', 'Mecanizada'


class TipoContrato(models.TextChoices):
    CLT = 'CLT', 'CLT'
    PJ = 'PJ', 'Pessoa Jurídica'
    ESTAGIARIO = 'ESTAGIARIO', 'Estagiário'
    TEMPORARIO = 'TEMPORARIO', 'Temporário'
    APRENDIZ = 'APRENDIZ', 'Jovem Aprendiz'


class StatusFuncionario(models.TextChoices):
    AGUARDANDO_ADMISSAO = 'AGUARDANDO_ADMISSAO', 'Aguardando Admissão'
    ATIVO = 'ATIVO', 'Ativo'
    AFASTADO = 'AFASTADO', 'Afastado'
    FERIAS = 'FERIAS', 'Em Férias'
    DEMITIDO = 'DEMITIDO', 'Demitido'


class TamanhoCamisa(models.TextChoices):
    PP = 'PP', 'PP'
    P = 'P', 'P'
    M = 'M', 'M'
    G = 'G', 'G'
    GG = 'GG', 'GG'
    XG = 'XG', 'XG'
    XGG = 'XGG', 'XGG'


class TamanhoCalca(models.TextChoices):
    NUM_36 = '36', '36'
    NUM_38 = '38', '38'
    NUM_40 = '40', '40'
    NUM_42 = '42', '42'
    NUM_44 = '44', '44'
    NUM_46 = '46', '46'
    NUM_48 = '48', '48'
    NUM_50 = '50', '50'
    NUM_52 = '52', '52'
    NUM_54 = '54', '54'
    NUM_56 = '56', '56'
    NUM_58 = '58', '58'
    NUM_60 = '60', '60'


class TamanhoCalcado(models.TextChoices):
    NUM_34 = '34', '34'
    NUM_35 = '35', '35'
    NUM_36 = '36', '36'
    NUM_37 = '37', '37'
    NUM_38 = '38', '38'
    NUM_39 = '39', '39'
    NUM_40 = '40', '40'
    NUM_41 = '41', '41'
    NUM_42 = '42', '42'
    NUM_43 = '43', '43'
    NUM_44 = '44', '44'
    NUM_45 = '45', '45'
    NUM_46 = '46', '46'
    NUM_47 = '47', '47'
    NUM_48 = '48', '48'
    NUM_49 = '49', '49'
    NUM_50 = '50', '50'


class TipoConta(models.TextChoices):
    CORRENTE = 'CORRENTE', 'Conta Corrente'
    POUPANCA = 'POUPANCA', 'Conta Poupança'
