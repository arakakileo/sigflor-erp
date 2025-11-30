# -*- coding: utf-8 -*-
from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError

from ..models import Cargo, CargoDocumento


class CargoDocumentoService:
    """Service layer para operações com CargoDocumento."""

    @staticmethod
    @transaction.atomic
    def configurar_documento_para_cargo(
        *,
        cargo: Cargo,
        documento_tipo: str,
        obrigatorio: bool = True,
        condicional: Optional[str] = None,
        created_by=None,
    ) -> CargoDocumento:
        """
        Configura um tipo de documento como requisito para um cargo.

        Se já existir configuração para este cargo/tipo, atualiza.
        Caso contrário, cria nova configuração.

        Args:
            cargo: Cargo ao qual o requisito se aplica
            documento_tipo: Tipo de documento (Documento.Tipo choices)
            obrigatorio: Se o documento é obrigatório
            condicional: Descrição de condições adicionais
            created_by: Usuário que está realizando a operação

        Returns:
            CargoDocumento: Instância criada ou atualizada
        """
        cargo_documento, created = CargoDocumento.objects.get_or_create(
            cargo=cargo,
            documento_tipo=documento_tipo,
            deleted_at__isnull=True,
            defaults={
                'obrigatorio': obrigatorio,
                'condicional': condicional,
                'created_by': created_by,
            }
        )

        if not created:
            cargo_documento.obrigatorio = obrigatorio
            cargo_documento.condicional = condicional
            cargo_documento.updated_by = created_by
            cargo_documento.save()

        return cargo_documento

    @staticmethod
    @transaction.atomic
    def update(
        cargo_documento: CargoDocumento,
        updated_by=None,
        **kwargs
    ) -> CargoDocumento:
        """Atualiza uma configuração de documento existente."""
        for attr, value in kwargs.items():
            if hasattr(cargo_documento, attr):
                setattr(cargo_documento, attr, value)

        cargo_documento.updated_by = updated_by
        cargo_documento.save()
        return cargo_documento

    @staticmethod
    @transaction.atomic
    def delete(cargo_documento: CargoDocumento, user=None) -> None:
        """Soft delete de uma configuração de documento."""
        cargo_documento.delete(user=user)

    @staticmethod
    def get_documentos_obrigatorios_para_cargo(cargo: Cargo) -> list:
        """
        Retorna todos os documentos obrigatórios para um cargo.

        Args:
            cargo: Cargo a consultar

        Returns:
            list: Lista de CargoDocumento obrigatórios
        """
        return list(CargoDocumento.objects.filter(
            cargo=cargo,
            obrigatorio=True,
            deleted_at__isnull=True
        ).order_by('documento_tipo'))

    @staticmethod
    def get_todos_documentos_para_cargo(cargo: Cargo) -> list:
        """
        Retorna todos os documentos configurados para um cargo.

        Args:
            cargo: Cargo a consultar

        Returns:
            list: Lista de CargoDocumento (obrigatórios e opcionais)
        """
        return list(CargoDocumento.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        ).order_by('obrigatorio', 'documento_tipo'))

    @staticmethod
    def validar_documentos_funcionario(funcionario) -> dict:
        """
        Valida se o funcionário possui todos os documentos obrigatórios.

        Args:
            funcionario: Instância do Funcionário

        Returns:
            dict: {
                'valido': bool,
                'documentos_ok': list,
                'documentos_faltantes': list,
                'documentos_opcionais_faltantes': list
            }
        """
        from apps.comum.models import PessoaFisicaDocumento

        cargo = funcionario.cargo
        pessoa_fisica = funcionario.pessoa_fisica

        # Obtém todos os documentos configurados para o cargo
        requisitos = CargoDocumento.objects.filter(
            cargo=cargo,
            deleted_at__isnull=True
        )

        # Obtém os tipos de documentos que o funcionário possui
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

    @staticmethod
    def copiar_requisitos_de_cargo(
        cargo_origem: Cargo,
        cargo_destino: Cargo,
        created_by=None
    ) -> list:
        """
        Copia os requisitos de documentos de um cargo para outro.

        Args:
            cargo_origem: Cargo de onde copiar
            cargo_destino: Cargo para onde copiar
            created_by: Usuário realizando a operação

        Returns:
            list: Lista de CargoDocumento criados
        """
        requisitos_origem = CargoDocumento.objects.filter(
            cargo=cargo_origem,
            deleted_at__isnull=True
        )

        novos_requisitos = []
        for req in requisitos_origem:
            novo, _ = CargoDocumento.objects.get_or_create(
                cargo=cargo_destino,
                documento_tipo=req.documento_tipo,
                deleted_at__isnull=True,
                defaults={
                    'obrigatorio': req.obrigatorio,
                    'condicional': req.condicional,
                    'created_by': created_by,
                }
            )
            novos_requisitos.append(novo)

        return novos_requisitos
