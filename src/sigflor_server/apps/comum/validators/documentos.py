from django.core.exceptions import ValidationError


def validar_cnpj(cnpj: str) -> None:
    """Valida CNPJ usando o algoritmo oficial."""
    if not cnpj or len(cnpj) != 14 or not cnpj.isdigit():
        raise ValidationError("CNPJ deve conter exatamente 14 dígitos numéricos.")

    if len(set(cnpj)) == 1:
        raise ValidationError("CNPJ inválido: todos os dígitos são iguais.")

    def calcular_digito(cnpj_base, pesos):
        soma = sum(int(cnpj_base[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cnpj[:12], pesos1)

    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cnpj[:13], pesos2)

    if int(cnpj[12]) != digito1 or int(cnpj[13]) != digito2:
        raise ValidationError("CNPJ inválido: dígitos verificadores incorretos.")


def validar_cpf(cpf: str) -> None:
    """Valida CPF usando o algoritmo oficial."""
    if not cpf or len(cpf) != 11 or not cpf.isdigit():
        raise ValidationError("CPF deve conter exatamente 11 dígitos numéricos.")

    if len(set(cpf)) == 1:
        raise ValidationError("CPF inválido: todos os dígitos são iguais.")

    def calcular_digito(cpf_base, pesos):
        soma = sum(int(cpf_base[i]) * pesos[i] for i in range(len(pesos)))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
    digito1 = calcular_digito(cpf[:9], pesos1)

    pesos2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
    digito2 = calcular_digito(cpf[:10], pesos2)

    if int(cpf[9]) != digito1 or int(cpf[10]) != digito2:
        raise ValidationError("CPF inválido: dígitos verificadores incorretos.")
