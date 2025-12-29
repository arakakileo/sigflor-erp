from django.db import transaction
from apps.autenticacao.models import Usuario
from rest_framework.exceptions import ValidationError

class UsuarioService:

    @staticmethod
    @transaction.atomic
    def create(*, user: Usuario, password: str, **dados_validos) -> Usuario:

        lista_papeis = dados_validos.pop('papeis', []) 
        lista_filiais = dados_validos.pop('allowed_filiais', [])
        lista_permissoes = dados_validos.pop('permissoes_diretas', [])

        novo_usuario = Usuario.objects.create_user(
            password=password,
            **dados_validos
        )

        if len(lista_papeis) > 0:
            novo_usuario.papeis.set(lista_papeis)
        
        if len(lista_filiais) > 0:
            novo_usuario.allowed_filiais.set(lista_filiais)

        if len(lista_permissoes) > 0:
            novo_usuario.permissoes_diretas.set(lista_permissoes)

        return novo_usuario

    @staticmethod
    @transaction.atomic
    def update(*, user: Usuario, usuario_para_editar: Usuario, **dados_novos) -> Usuario:
        
        if 'password' in dados_novos:
            del dados_novos['password']
        
        # 1. Extraindo listas (se vier None, é porque o front não mandou alterar)
        lista_papeis = dados_novos.pop('papeis', None)
        lista_filiais = dados_novos.pop('allowed_filiais', None)
        lista_permissoes = dados_novos.pop('permissoes_diretas', None) # <--- NOVO

        # 2. Atualizando campos de texto
        for campo, valor in dados_novos.items():
            if hasattr(usuario_para_editar, campo):
                setattr(usuario_para_editar, campo, valor)
        
        usuario_para_editar.save()

        # 3. Atualizando relacionamentos
        if lista_papeis is not None:
            usuario_para_editar.papeis.set(lista_papeis)
            
        if lista_filiais is not None:
            usuario_para_editar.allowed_filiais.set(lista_filiais)

        if lista_permissoes is not None: # <--- Lógica Nova
            usuario_para_editar.permissoes_diretas.set(lista_permissoes)

        return usuario_para_editar

    @staticmethod
    @transaction.atomic
    def delete(*, user: Usuario, usuario_para_deletar: Usuario) -> None:
        # Chama o método delete customizado do Model (Soft Delete)
        usuario_para_deletar.delete(user=user)

    @staticmethod
    @transaction.atomic
    def redefinir_senha(*, user: Usuario, usuario_alvo: Usuario, nova_senha: str) -> None:
        # set_password faz a criptografia (hash)
        usuario_alvo.set_password(nova_senha)
        usuario_alvo.save()

    @staticmethod
    @transaction.atomic
    def alterar_senha_proprio_usuario(*, user: Usuario, senha_atual: str, nova_senha: str) -> None:
        senha_correta = user.check_password(senha_atual)
        if not senha_correta:
            raise ValidationError({"senha_atual": "A senha atual informada está incorreta."})
        user.set_password(nova_senha)
        user.save()