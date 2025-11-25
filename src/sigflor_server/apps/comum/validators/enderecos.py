from django.core.exceptions import ValidationError


class EnderecoValidator:
    @staticmethod
    def _somente_digitos(s: str) -> str:
        return ''.join(ch for ch in (s or '') if ch.isdigit())

    @staticmethod
    def normalizar(instance) -> None:
        instance.logradouro = (instance.logradouro or '').strip()
        instance.numero = (instance.numero or '').strip() or None
        instance.complemento = (instance.complemento or '').strip() or None
        instance.bairro = (instance.bairro or '').strip() or None
        instance.cidade = (instance.cidade or '').strip()
        instance.pais = (instance.pais or '').strip() or 'Brasil'
        instance.estado = (instance.estado or '').strip().upper()
        instance.cep = EnderecoValidator._somente_digitos(instance.cep)

        if instance.estado and instance.estado not in instance.UF.values:
            raise ValidationError({'estado': 'UF inválida.'})
        if len(instance.cep) != 8:
            raise ValidationError({'cep': 'CEP deve ter 8 dígitos (somente números).'})
        if not instance.logradouro:
            raise ValidationError({'logradouro': 'Logradouro é obrigatório.'})
        if not instance.cidade:
            raise ValidationError({'cidade': 'Cidade é obrigatória.'})
