from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.sst.services import ExameService, EPIService
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
        epis_obrigatorios: list = None,
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
                CargoDocumentoService.vincular_documento_cargo(
                    cargo=cargo,
                    user=user,
                    **doc_data
                )

        if exames_obrigatorios:
            for exame_data in exames_obrigatorios:
                ExameService.vincular_exame_cargo(
                    cargo=cargo,
                    user=user,
                    **exame_data
                )

        if epis_obrigatorios:
            for epi_data in epis_obrigatorios:
                EPIService.vincular_epi_cargo(
                    cargo=cargo,
                    user=user,
                    **epi_data
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
        epis_obrigatorios: list = None,
        **kwargs
    ) -> Cargo:

        for attr, value in kwargs.items():
            if hasattr(cargo, attr):
                setattr(cargo, attr, value)

        cargo.updated_by = user
        cargo.save()

        if documentos_obrigatorios is not None:
            CargoDocumentoService.atualizar_vinculos_documentos_cargo(
                cargo=cargo,
                documentos_data=documentos_obrigatorios,
                user=user
            )

        if exames_obrigatorios is not None:
            ExameService.atualizar_vinculos_exames_cargo(
                cargo=cargo,
                exames_data=exames_obrigatorios,
                user=user
            )
            
        if epis_obrigatorios is not None:
            EPIService.atualizar_vinculos_epis_cargo(
                cargo=cargo,
                epis_data=epis_obrigatorios,
                user=user
            )

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