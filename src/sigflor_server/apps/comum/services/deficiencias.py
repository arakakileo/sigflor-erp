# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from django.db import transaction
from datetime import timedelta
from django.db.models import QuerySet
from rest_framework.exceptions import ValidationError

from ..models import Deficiencia, PessoaFisica, PessoaFisicaDeficiencia
from ..models.enums import TipoDeficiencia
from apps.autenticacao.models import Usuario


class DeficienciaService:

    @staticmethod
    @transaction.atomic
    def create(
        *,
        nome: str,
        created_by: Usuario,
        tipo: str = TipoDeficiencia.OUTRA,
        cid: str = '',
        descricao: str = '',
    ) -> Deficiencia:
        deficiencia = Deficiencia(
            nome=nome,
            tipo=tipo,
            cid=cid,
            descricao=descricao,
            created_by=created_by,
        )
        deficiencia.save()
        return deficiencia

    @staticmethod
    @transaction.atomic
    def update(
        deficiencia: Deficiencia, 
        updated_by: Usuario,
        **kwargs: Any
    ) -> Deficiencia:
        for attr, value in kwargs.items():
            if hasattr(deficiencia, attr):
                setattr(deficiencia, attr, value)
        
        deficiencia.updated_by = updated_by
        deficiencia.save()
        return deficiencia

    @staticmethod
    @transaction.atomic
    def delete(deficiencia: Deficiencia, user: Usuario) -> None:
        if deficiencia.vinculos_pessoa_fisica.filter(deleted_at__isnull=True).exists():
            raise ValidationError("Não é possível excluir uma deficiência que está vinculada a pessoas ativas.")

        deficiencia.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(deficiencia: Deficiencia, user: Usuario) -> None:
        deficiencia.restore(user=user)

class PessoaFisicaDeficienciaService:

    @staticmethod
    def get_vinculos_pessoa_fisica(pessoa_fisica: PessoaFisica) -> QuerySet[PessoaFisicaDeficiencia]:
        return PessoaFisicaDeficiencia.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__isnull=True
        ).select_related('deficiencia')

    @staticmethod
    @transaction.atomic
    def create_vinculo(
        *,
        pessoa_fisica: PessoaFisica,
        deficiencia: Deficiencia,
        created_by: Usuario,
        grau: str = '',
        congenita: bool = False,
        observacoes: str = '',
    ) -> PessoaFisicaDeficiencia:
        
        if PessoaFisicaDeficiencia.objects.filter(
            pessoa_fisica=pessoa_fisica, 
            deficiencia=deficiencia, 
            deleted_at__isnull=True
        ).exists():
            raise ValidationError(f"A deficiência '{deficiencia.nome}' já está vinculada a esta pessoa.")

        vinculo = PessoaFisicaDeficiencia(
            pessoa_fisica=pessoa_fisica,
            deficiencia=deficiencia,
            grau=grau,
            congenita=congenita,
            observacoes=observacoes,
            created_by=created_by,
        )
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def update_vinculo(
        vinculo: PessoaFisicaDeficiencia, 
        updated_by: Usuario,
        **kwargs: Any
    ) -> PessoaFisicaDeficiencia:
        campos = ['grau', 'congenita', 'observacoes']
        for attr, value in kwargs.items():
            if attr in campos and hasattr(vinculo, attr):
                setattr(vinculo, attr, value)
        
        vinculo.updated_by = updated_by
        vinculo.save()
        return vinculo

    @staticmethod
    @transaction.atomic
    def delete_vinculo(vinculo: PessoaFisicaDeficiencia, user: Usuario) -> None:
        vinculo.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore_vinculo(vinculo: PessoaFisicaDeficiencia, user: Usuario) -> None:
        vinculo.restore(user=user)

    @classmethod
    def restaurar_deficiencias_pessoa_fisica(
        cls, 
        pessoa_fisica: PessoaFisica, 
        data_delecao_pai: Any, 
        user: Usuario
    ) -> None:
        
        if not data_delecao_pai:
            return

        margem = timedelta(seconds=5)
        inicio = data_delecao_pai - margem
        fim = data_delecao_pai + margem

        vinculos = PessoaFisicaDeficiencia.objects.filter(
            pessoa_fisica=pessoa_fisica,
            deleted_at__range=(inicio, fim)
        )

        for vinculo in vinculos:
            vinculo.restore(user=user)

    @classmethod
    @transaction.atomic
    def sincronizar_deficiencias_pessoa_fisica(
        cls, 
        pessoa_fisica: PessoaFisica, 
        lista_deficiencias: List[Dict[str, Any]], 
        user: Usuario
    ) -> None:

        if lista_deficiencias is None:
            return

        ids_recebidos = [str(item['id']) for item in lista_deficiencias if item.get('id')]
        if len(ids_recebidos) != len(set(ids_recebidos)):
            raise ValidationError({"non_field_errors": ["IDs de vínculos duplicados na requisição."]})
        ids_recebidos_set = set(ids_recebidos)

        existentes_qs = cls.get_vinculos_pessoa_fisica(pessoa_fisica)
        existentes_map = {str(v.id): v for v in existentes_qs}

        cls._validar_duplicidade_catalogo(existentes_map, lista_deficiencias)

        # Deleções
        for vinculo_id, vinculo in existentes_map.items():
            if vinculo_id not in ids_recebidos_set:
                cls.delete_vinculo(vinculo, user=user)

        # Criações e Atualizações
        for item in lista_deficiencias:
            vinculo_id = str(item.get('id')) if item.get('id') else None

            if vinculo_id and vinculo_id not in existentes_map:
                raise ValidationError({"deficiencias": [f"O vínculo de deficiência '{vinculo_id}' não pertence a esta pessoa."]})

            if not vinculo_id:
                deficiencia_obj = item.get('deficiencia_id') if 'deficiencia_id' in item else item.get('deficiencia')
                
                cls.create_vinculo(
                    pessoa_fisica=pessoa_fisica,
                    created_by=user,
                    deficiencia=deficiencia_obj,
                    grau=item.get('grau', ''),
                    congenita=item.get('congenita', False),
                    observacoes=item.get('observacoes', '')
                )
                continue

            vinculo = existentes_map[vinculo_id]
            nova_deficiencia = item.get('deficiencia') or item.get('deficiencia_id')
            if nova_deficiencia and nova_deficiencia != vinculo.deficiencia:
                raise ValidationError({"deficiencias": ["Não é permitido alterar o tipo de deficiência de um vínculo existente. Remova e adicione novamente."]})

            cls.update_vinculo(vinculo, updated_by=user, **item)

    @staticmethod
    def _validar_duplicidade_catalogo(existentes_map: Dict[str, PessoaFisicaDeficiencia], lista_itens: List[Dict[str, Any]]) -> None:

        deficiencias_payload = set()
        for item in lista_itens:
            deficiencia_obj = item.get('deficiencia') or item.get('deficiencia_id')
            
            if not deficiencia_obj:
                continue 
            
            deficiencia_id = str(deficiencia_obj.id) if hasattr(deficiencia_obj, 'id') else str(deficiencia_obj)
            
            if deficiencia_id in deficiencias_payload:
                nome_erro = deficiencia_obj.nome if hasattr(deficiencia_obj, 'nome') else "informada"
                raise ValidationError({"deficiencias": [f"A deficiência '{nome_erro}' foi enviada mais de uma vez."]})
            deficiencias_payload.add(deficiencia_id)

        for item in lista_itens:
            vinculo_id = str(item.get('id')) if item.get('id') else None
            deficiencia_obj = item.get('deficiencia') or item.get('deficiencia_id')
            
            if not deficiencia_obj: continue

            target_id = deficiencia_obj.id if hasattr(deficiencia_obj, 'id') else deficiencia_obj

            for v_id, vinculo in existentes_map.items():
                if vinculo.deficiencia_id == target_id and v_id != vinculo_id:
                    raise ValidationError({"deficiencias": [f"A deficiência '{vinculo.deficiencia.nome}' já está vinculada a esta pessoa."]})