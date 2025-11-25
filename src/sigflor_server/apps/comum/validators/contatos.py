from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


class ContatosValidator:
    DDD_VALIDOS = {
        # Sudeste
        11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
        # Sul
        41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55,
        # Centro-Oeste
        61, 62, 64, 65, 66, 67, 68, 69,
        # Nordeste
        71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89,
        # Norte
        91, 92, 93, 94, 95, 96, 97, 98, 99,
    }

    @staticmethod
    def normalizar_email(value: str) -> str:
        v = (value or '').strip().lower()
        EmailValidator(message='E-mail inválido', code='email_invalido')(v)
        return v

    @staticmethod
    def normalizar_telefone_fixo(value: str) -> str:
        digitos = ''.join(ch for ch in (value or '') if ch.isdigit())
        if len(digitos) != 10:
            raise ValidationError(
                {'telefone_fixo': 'Números de Telefones Fixo devem ter 10 dígitos.'},
                code='tamanho_invalido'
            )
        ddd = digitos[:2]
        if int(ddd) not in ContatosValidator.DDD_VALIDOS:
            raise ValidationError({'ddd': 'DDD inválido.'}, code='ddd_invalido')
        if digitos[2] not in '2345':
            raise ValidationError(
                {'telefone_fixo': 'Telefone fixo inválido. Devem começar com 2, 3, 4 ou 5'},
                code='prefixo_invalido'
            )
        return digitos

    @staticmethod
    def normalizar_telefone_celular(value: str) -> str:
        digitos = ''.join(ch for ch in (value or '') if ch.isdigit())
        if digitos.startswith('55') and len(digitos) >= 12:
            digitos = digitos[2:]
        if digitos.startswith('0') and len(digitos) in (11, 12):
            digitos = digitos[1:]
        if len(digitos) != 11:
            raise ValidationError(
                {'telefone_celular': 'Números de Celular devem ter 11 dígitos.'},
                code='tamanho_invalido'
            )
        ddd = digitos[:2]
        if int(ddd) not in ContatosValidator.DDD_VALIDOS:
            raise ValidationError({'ddd': 'DDD inválido.'}, code='ddd_invalido')
        if digitos[2] != '9':
            raise ValidationError(
                {'telefone_celular': 'Números de Celular devem iniciar com 9.'},
                code='prefixo_invalido'
            )
        return digitos
