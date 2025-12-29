# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from apps.comum.views.base import BaseRBACViewSet
from apps.autenticacao.models import Usuario
from ..serializers import (
    UsuarioListSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    UsuarioRedefinirSenhaSerializer,
    UsuarioAlterarMinhaSenhaSerializer
)
from ..services import UsuarioService
from .. import selectors

class UsuarioViewSet(BaseRBACViewSet):

    permissao_leitura = 'autenticacao.view_usuario'
    permissao_update = 'autenticacao.change_usuario'
    permissao_create = 'autenticacao.add_usuario'
    permissao_delete = 'autenticacao.delete_usuario'

    permissoes_acoes = {
        'redefinir_senha': 'autenticacao.change_usuario', # Só admin pode resetar senha
        'me': None,
        'alterar_minha_senha': None,
        'destroy': 'autenticacao.delete_usuario'
    }

    queryset = Usuario.objects.filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        if self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        if self.action == 'redefinir_senha':
            return UsuarioRedefinirSenhaSerializer
        if self.action == 'alterar_minha_senha':
            return UsuarioAlterarMinhaSenhaSerializer
        return UsuarioListSerializer

    def get_queryset(self):
        termo_busca = self.request.query_params.get('search')
        status_ativo = self.request.query_params.get('ativo')
        filtro_papel = self.request.query_params.get('papel')

        return selectors.usuario_list(
            user=self.request.user,
            busca=termo_busca,
            ativo=status_ativo,
            papel_id=filtro_papel
        )

    def perform_create(self, serializer):
        dados_do_formulario = serializer.validated_data
        UsuarioService.create(
            user=self.request.user,
            **dados_do_formulario
        )

    def perform_update(self, serializer):
        """
        Executado quando o PUT/PATCH é enviado para editar um usuário.
        """
        usuario_que_sera_editado = serializer.instance
        dados_novos = serializer.validated_data

        UsuarioService.update(
            user=self.request.user,
            usuario_para_editar=usuario_que_sera_editado,
            **dados_novos
        )

    def perform_destroy(self, instance):
        """
        Executado quando o DELETE é enviado.
        """
        usuario_que_sera_deletado = instance
        
        UsuarioService.delete(
            user=self.request.user,
            usuario_para_deletar=usuario_que_sera_deletado
        )

    # --- ACTIONS EXTRAS ---

    @action(detail=True, methods=['post'], url_path='redefinir-senha')
    def redefinir_senha(self, request, pk=None):
        """
        Rota para Admin resetar a senha de outro usuário.
        URL: POST /api/auth/usuarios/{id}/redefinir-senha/
        """
        # 1. Pega o usuário alvo pelo ID da URL
        usuario_alvo = self.get_object()
        
        # 2. Valida os dados enviados (nova_senha)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        nova_senha = serializer.validated_data['nova_senha']

        # 3. Chama o Service para criptografar e salvar
        UsuarioService.redefinir_senha(
            user=request.user, # Quem está fazendo a ação (Admin)
            usuario_alvo=usuario_alvo, # Quem vai ter a senha trocada
            nova_senha=nova_senha
        )
        
        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        usuario_logado = request.user
        serializer = UsuarioListSerializer(usuario_logado)
        dados_resposta = serializer.data
        dados_resposta['permissoes'] = usuario_logado.get_all_permissions()
        return Response(dados_resposta, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='alterar-minha-senha')
    def alterar_minha_senha(self, request):
        usuario_logado = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        dados = serializer.validated_data

        UsuarioService.alterar_senha_proprio_usuario(
            user=usuario_logado,
            senha_atual=dados['senha_atual'],
            nova_senha=dados['nova_senha']
        )
        
        return Response({'detail': 'Sua senha foi alterada com sucesso.'}, status=status.HTTP_200_OK)