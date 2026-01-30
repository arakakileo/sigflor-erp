# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Cargo, CargoDocumento


class CargoDocumentoService:

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
        condicional: Optional[str] = '',
        user=None,
    ) -> CargoDocumento:
        """
        Cria ou atualiza um vínculo de documento para um cargo.
        """
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
    def remover_vinculo_documento_cargo(cargo_documento: CargoDocumento, user=None) -> None:
        """
        Remove (soft delete) um vínculo de documento do cargo.
        """
        cargo_documento.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restaurar_vinculos_documentos_cargo(cargo, data_delecao, user):
        """
        Restaura vínculos deletados em cascading.
        """
        # Implementação futura se necessário cascading restore manual
        pass

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
            
            doc = CargoDocumentoService.vincular_documento_cargo(
                cargo=cargo,
                user=user,
                **data
            )
            resultado.append(doc)

        for tipo, doc_existente in existentes.items():
            if tipo not in processados_tipos:
                CargoDocumentoService.remover_vinculo_documento_cargo(doc_existente, user=user)
        
        return resultado

    @staticmethod
    def validar_documentos_funcionario(funcionario) -> dict:
        """
        Valida se o funcionário possui todos os documentos obrigatórios.
        """
        from apps.comum.models import PessoaFisicaDocumento

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
