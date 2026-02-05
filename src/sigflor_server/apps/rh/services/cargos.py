from django.db import transaction
from django.core.exceptions import ValidationError

from apps.autenticacao.models import Usuario
from apps.comum.models import PessoaFisicaDocumento
from apps.sst.services import ExameService, EPIService
from ..models import Cargo, CargoDocumento

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
                CargoService.vincular_documento_cargo(
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
            CargoService.atualizar_vinculos_documentos_cargo(
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

    # ============================================================================
    # Gestão de Documentos (Anteriormente em CargoDocumentoService)
    # ============================================================================

    @staticmethod
    def get_documentos_cargo(cargo: Cargo) -> list:
        """
        Retorna todos os documentos configurados para um cargo.
        """
        return list(CargoDocumento.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        ).order_by('obrigatorio', 'documento_tipo'))

    @staticmethod
    @transaction.atomic
    def vincular_documento_cargo(
        *,
        cargo: Cargo,
        documento_tipo: str,
        obrigatorio: bool = True,
        condicional: str = '',
        user=None,
    ):
        cargo_documento, created = CargoDocumento.objects.get_or_create(
            cargo=cargo,
            documento_tipo=documento_tipo,
            deleted_at__isnull=True,
            defaults={
                'obrigatorio': obrigatorio,
                'condicional': condicional,
                'created_by': user,
            }
        )

        if not created:
            cargo_documento.obrigatorio = obrigatorio
            cargo_documento.condicional = condicional
            cargo_documento.save()

        return cargo_documento

    @staticmethod
    @transaction.atomic
    def remover_vinculo_documento_cargo(cargo_documento, user=None) -> None:
        """
        Remove (soft delete) um vínculo de documento do cargo.
        """
        cargo_documento.delete(user=user)

    @staticmethod
    @transaction.atomic
    def atualizar_vinculos_documentos_cargo(
        *,
        cargo: Cargo,
        documentos_data: list,
        user
    ) -> list:
        """
        Sincroniza a lista de documentos (Full Sync).
        """
        if documentos_data is None:
            documentos_data = []

        existentes = {
            doc.documento_tipo: doc 
            for doc in CargoDocumento.objects.filter(cargo=cargo, deleted_at__isnull=True)
        }
        
        processados_tipos = set()
        resultado = []

        for data in documentos_data:
            tipo = data.get('documento_tipo')
            if not tipo: continue
            
            processados_tipos.add(tipo)
            
            # Chama o próprio método estático da classe
            doc = CargoService.vincular_documento_cargo(
                cargo=cargo,
                user=user,
                **data
            )
            resultado.append(doc)

        for tipo, doc_existente in existentes.items():
            if tipo not in processados_tipos:
                CargoService.remover_vinculo_documento_cargo(doc_existente, user=user)
        
        return resultado

    @staticmethod
    def validar_documentos_funcionario(funcionario) -> dict:
        """
        Valida se o funcionário possui todos os documentos obrigatórios.
        """

        cargo = funcionario.cargo
        pessoa_fisica = funcionario.pessoa_fisica

        requisitos = CargoDocumento.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        )

        documentos_funcionario = set(
            PessoaFisicaDocumento.objects.filter(
                pessoa_fisica=pessoa_fisica,
                deleted_at__isnull=True
            ).values_list('documento__tipo', flat=True)
        )

        documentos_ok = []
        documentos_faltantes = []
        documentos_opcionais_faltantes = []

        for req in requisitos:
            if req.documento_tipo in documentos_funcionario:
                documentos_ok.append({
                    'tipo': req.documento_tipo,
                    'tipo_display': req.tipo_display,
                    'obrigatorio': req.obrigatorio,
                })
            else:
                item = {
                    'tipo': req.documento_tipo,
                    'tipo_display': req.tipo_display,
                    'obrigatorio': req.obrigatorio,
                    'condicional': req.condicional,
                }
                if req.obrigatorio:
                    documentos_faltantes.append(item)
                else:
                    documentos_opcionais_faltantes.append(item)

        return {
            'valido': len(documentos_faltantes) == 0,
            'documentos_ok': documentos_ok,
            'documentos_faltantes': documentos_faltantes,
            'documentos_opcionais_faltantes': documentos_opcionais_faltantes,
        }