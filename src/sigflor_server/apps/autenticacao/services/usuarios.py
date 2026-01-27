from django.db import transaction
from apps.autenticacao.models import Usuario

class UsuarioService:

    @staticmethod
    @transaction.atomic
    def create(*, user: Usuario, password: str, **dados_validos) -> Usuario:

        if not dados_validos['username']:
            dados_validos['username'] = dados_validos['email']

        lista_papeis = dados_validos.pop('papeis', []) 
        lista_filiais = dados_validos.pop('allowed_filiais', [])
        lista_permissoes = dados_validos.pop('user_permissions', [])

        novo_usuario = Usuario.objects.create_user(
            password=password,
            created_by=user,
            **dados_validos
        )

        if len(lista_papeis) > 0:
            novo_usuario.papeis.set(lista_papeis)
        
        if len(lista_filiais) > 0:
            novo_usuario.allowed_filiais.set(lista_filiais)

        if len(lista_permissoes) > 0:
            novo_usuario.user_permissions.set(lista_permissoes)

        return novo_usuario

    @staticmethod
    @transaction.atomic
    def update(*, user: Usuario, usuario_para_editar: Usuario, **dados_novos) -> Usuario:
        if 'password' in dados_novos:
            del dados_novos['password']
        
        lista_papeis = dados_novos.pop('papeis', None)
        lista_filiais = dados_novos.pop('allowed_filiais', None)
        lista_permissoes = dados_novos.pop('user_permissions', None)

        for campo, valor in dados_novos.items():
            if hasattr(usuario_para_editar, campo):
                setattr(usuario_para_editar, campo, valor)
        
        if hasattr(usuario_para_editar, 'updated_by'):
            usuario_para_editar.updated_by = user

        usuario_para_editar.save()

        if lista_papeis is not None:
            usuario_para_editar.papeis.set(lista_papeis)
            
        if lista_filiais is not None:
            usuario_para_editar.allowed_filiais.set(lista_filiais)

        if lista_permissoes is not None:
            usuario_para_editar.user_permissions.set(lista_permissoes)

        return usuario_para_editar

    @staticmethod
    @transaction.atomic
    def delete(*, user: Usuario, usuario_para_deletar: Usuario) -> None:
        usuario_para_deletar.delete(user=user)

    @staticmethod
    @transaction.atomic
    def restore(*, user: Usuario, usuario_para_restaurar: Usuario) -> None:
        usuario_para_restaurar.restore(user=user)

    @staticmethod
    @transaction.atomic
    def redefinir_senha(*, user: Usuario, usuario_alvo: Usuario, nova_senha: str) -> None:
        usuario_alvo.set_password(nova_senha)
        if hasattr(usuario_alvo, 'updated_by'):
            usuario_alvo.updated_by = user
        usuario_alvo.save()

    @staticmethod
    @transaction.atomic
    def alterar_senha_proprio_usuario(*, user: Usuario, senha_atual: str, nova_senha: str) -> None:
        """
        O próprio usuário altera sua senha.
        """
        from rest_framework.exceptions import ValidationError
        senha_correta = user.check_password(senha_atual)
        if not senha_correta:
            raise ValidationError({"senha_atual": "A senha atual informada está incorreta."})
        user.set_password(nova_senha)
        if hasattr(user, 'updated_by'):
            user.updated_by = user
        user.save()