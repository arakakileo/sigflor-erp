from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.sst.services import ExameService
from .cargo_documento import CargoDocumentoService
from ..models import Cargo


class CargoService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        user: Usuario,
        nome: str,
        nivel: str,
        documentos_obrigatorios: list = None,
        exames_obrigatorios: list = None,
        **kwargs
    ) -> Cargo:

        cargo = Cargo(
            nome=nome,
            nivel=nivel,
            created_by=user,
            **kwargs
        )

        cargo.save()

        if documentos_obrigatorios:
            for doc_data in documentos_obrigatorios:
                CargoDocumentoService.configurar_documento_para_cargo(
                    cargo=cargo,
                    created_by=user,
                    **doc_data
                )
        
        if exames_obrigatorios:
            for exame_data in exames_obrigatorios:
                ExameService.configurar_exame_para_cargo(
                    cargo=cargo,
                    created_by=user,
                    **exame_data
                )

        return cargo

    @staticmethod
    @transaction.atomic
    def update(
        *,
        cargo: Cargo,
        user: Usuario,
        documentos_obrigatorios: list = None,
        exames_obrigatorios: list = None,
        **kwargs
    ) -> Cargo:
        
        for attr, value in kwargs.items():
            if hasattr(cargo, attr):
                setattr(cargo, attr, value)
        
        cargo.updated_by = user
        cargo.save()

        if documentos_obrigatorios is not None: ...

        if exames_obrigatorios is not None: ...


        return cargo

    @staticmethod
    @transaction.atomic
    def delete(cargo: Cargo, user: Usuario) -> None:
        if cargo.funcionarios.filter(deleted_at__isnull=True).exists():
            raise ValidationError(
                'Não é possível excluir um cargo que possui funcionários ativos vinculados.'
            )
        cargo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(cargo: Cargo, user: Usuario) -> Cargo:
        cargo.restore(user=user)
        return cargo

    @staticmethod
    @transaction.atomic
    def ativar(cargo: Cargo, updated_by: Usuario) -> Cargo:
        cargo.ativo = True
        cargo.updated_by = updated_by
        cargo.save()
        return cargo

    @staticmethod
    @transaction.atomic
    def desativar(cargo: Cargo, updated_by: Usuario) -> Cargo:
        cargo.ativo = False
        cargo.updated_by = updated_by
        cargo.save()
        return cargo