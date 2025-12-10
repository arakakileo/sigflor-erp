from typing import Optional
from django.db import transaction
from django.db.models import QuerySet

from ..models import (
    Endereco, TipoEndereco,
    PessoaFisicaEndereco, PessoaJuridicaEndereco, FilialEndereco,
    PessoaFisica, PessoaJuridica, Filial
)


class EnderecoService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        created_by=None,
    ) -> Endereco:
        """Cria um novo Endereço (sem vínculo com entidade)."""
        endereco = Endereco(
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            created_by=created_by,
        )
        endereco.save()
        return endereco

    @staticmethod
    @transaction.atomic
    def criar_endereco_pessoa_fisica(
        *,
        pessoa_fisica: PessoaFisica,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.RESIDENCIAL,
        principal: bool = False,
        created_by=None,
    ) -> PessoaFisicaEndereco:
        """
        Cria um endereço e vincula a uma PessoaFisica.
        Se principal=True, desmarca outros endereços do mesmo tipo como principal.
        """
        # Cria o endereço
        endereco = EnderecoService.create(
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            created_by=created_by,
        )

        # Se é principal, desmarca outros do mesmo tipo
        if principal:
            PessoaFisicaEndereco.objects.filter(
                pessoa_fisica=pessoa_fisica,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        # Cria o vínculo
        vinculo = PessoaFisicaEndereco(
            pessoa_fisica=pessoa_fisica,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def criar_endereco_pessoa_juridica(
        *,
        pessoa_juridica: PessoaJuridica,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.COMERCIAL,
        principal: bool = False,
        created_by=None,
    ) -> PessoaJuridicaEndereco:
        """
        Cria um endereço e vincula a uma PessoaJuridica.
        Se principal=True, desmarca outros endereços do mesmo tipo como principal.
        """
        endereco = EnderecoService.create(
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            created_by=created_by,
        )

        if principal:
            PessoaJuridicaEndereco.objects.filter(
                pessoa_juridica=pessoa_juridica,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = PessoaJuridicaEndereco(
            pessoa_juridica=pessoa_juridica,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def criar_endereco_filial(
        *,
        filial: Filial,
        logradouro: str,
        cidade: str,
        estado: str,
        cep: str,
        numero: Optional[str] = None,
        complemento: Optional[str] = None,
        bairro: Optional[str] = None,
        pais: str = 'Brasil',
        tipo: str = TipoEndereco.COMERCIAL,
        principal: bool = False,
        created_by=None,
    ) -> FilialEndereco:
        """
        Cria um endereço e vincula a uma Filial.
        Se principal=True, desmarca outros endereços do mesmo tipo como principal.
        """
        endereco = EnderecoService.create(
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            pais=pais,
            created_by=created_by,
        )

        if principal:
            FilialEndereco.objects.filter(
                filial=filial,
                tipo=tipo,
                principal=True,
                deleted_at__isnull=True
            ).update(principal=False)

        vinculo = FilialEndereco(
            filial=filial,
            endereco=endereco,
            tipo=tipo,
            principal=principal,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def set_principal_pessoa_fisica(
        *,
        vinculo: PessoaFisicaEndereco,
        updated_by=None,
    ) -> PessoaFisicaEndereco:
        """Define um endereço como principal para uma PessoaFisica."""
        PessoaFisicaEndereco.objects.filter(
            pessoa_fisica=vinculo.pessoa_fisica,
            tipo=vinculo.tipo,
            principal=True,
            deleted_at__isnull=True
        ).exclude(pk=vinculo.pk).update(principal=False)

        vinculo.principal = True
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def set_principal_pessoa_juridica(
        *,
        vinculo: PessoaJuridicaEndereco,
        updated_by=None,
    ) -> PessoaJuridicaEndereco:
        """Define um endereço como principal para uma PessoaJuridica."""
        PessoaJuridicaEndereco.objects.filter(
            pessoa_juridica=vinculo.pessoa_juridica,
            tipo=vinculo.tipo,
            principal=True,
            deleted_at__isnull=True
        ).exclude(pk=vinculo.pk).update(principal=False)

        vinculo.principal = True
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def set_principal_filial(
        *,
        vinculo: FilialEndereco,
        updated_by=None,
    ) -> FilialEndereco:
        """Define um endereço como principal para uma Filial."""
        FilialEndereco.objects.filter(
            filial=vinculo.filial,
            tipo=vinculo.tipo,
            principal=True,
            deleted_at__isnull=True
        ).exclude(pk=vinculo.pk).update(principal=False)

        vinculo.principal = True
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def update(endereco: Endereco, updated_by=None, **kwargs) -> Endereco:
        """Atualiza um Endereço existente."""
        allowed_fields = [
            'logradouro', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'cep', 'pais'
        ]
        for attr, value in kwargs.items():
            if attr in allowed_fields and hasattr(endereco, attr):
                setattr(endereco, attr, value)
        endereco.updated_by = updated_by
        endereco.save()
        return endereco

    @staticmethod
    @transaction.atomic
    def delete(endereco: Endereco, user=None) -> None:
        """Soft delete de um Endereço e seus vínculos."""
        from django.utils import timezone
        now = timezone.now()

        PessoaFisicaEndereco.objects.filter(
            endereco=endereco,
            deleted_at__isnull=True
        ).update(deleted_at=now)
        PessoaJuridicaEndereco.objects.filter(
            endereco=endereco,
            deleted_at__isnull=True
        ).update(deleted_at=now)
        FilialEndereco.objects.filter(
            endereco=endereco,
            deleted_at__isnull=True
        ).update(deleted_at=now)

        endereco.delete(user=user)

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_fisica(vinculo: PessoaFisicaEndereco, user=None) -> None:
        """Remove o vínculo de um endereço com uma PessoaFisica."""
        vinculo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def remove_vinculo_pessoa_juridica(vinculo: PessoaJuridicaEndereco, user=None) -> None:
        """Remove o vínculo de um endereço com uma PessoaJuridica."""
        vinculo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def remove_vinculo_filial(vinculo: FilialEndereco, user=None) -> None:
        """Remove o vínculo de um endereço com uma Filial."""
        vinculo.delete(user=user)

    @staticmethod
    def get_enderecos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet:
        """Retorna todos os endereços de uma PessoaFisica."""
        return PessoaFisicaEndereco.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    def get_enderecos_pessoa_juridica(pessoa_juridica: PessoaJuridica) -> QuerySet:
        """Retorna todos os endereços de uma PessoaJuridica."""
        return PessoaJuridicaEndereco.objects.filter(
            pessoa_juridica=pessoa_juridica,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    def get_enderecos_filial(filial: Filial) -> QuerySet:
        """Retorna todos os endereços de uma Filial."""
        return FilialEndereco.objects.filter(
            filial=filial,
            deleted_at__isnull=True
        ).select_related('endereco').order_by('tipo', '-principal', '-created_at')

    @staticmethod
    def get_endereco_principal_pessoa_fisica(
        pessoa_fisica: PessoaFisica,
        tipo: str = None
    ) -> Optional[PessoaFisicaEndereco]:
        """Retorna o endereço principal de uma PessoaFisica."""
        qs = PessoaFisicaEndereco.objects.filter(
            pessoa_fisica=pessoa_fisica,
            principal=True,
            deleted_at__isnull=True
        ).select_related('endereco')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.first()

    @staticmethod
    def get_endereco_principal_pessoa_juridica(
        pessoa_juridica: PessoaJuridica,
        tipo: str = None
    ) -> Optional[PessoaJuridicaEndereco]:
        """Retorna o endereço principal de uma PessoaJuridica."""
        qs = PessoaJuridicaEndereco.objects.filter(
            pessoa_juridica=pessoa_juridica,
            principal=True,
            deleted_at__isnull=True
        ).select_related('endereco')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.first()

    @staticmethod
    def get_endereco_principal_filial(
        filial: Filial,
        tipo: str = None
    ) -> Optional[FilialEndereco]:
        """Retorna o endereço principal de uma Filial."""
        qs = FilialEndereco.objects.filter(
            filial=filial,
            principal=True,
            deleted_at__isnull=True
        ).select_related('endereco')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.first()
