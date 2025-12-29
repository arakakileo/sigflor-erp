import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('O username é obrigatório')
        if not email:
            raise ValueError('O email é obrigatório')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('ativo', True)
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    ativo = models.BooleanField(default=True, help_text='Controla acesso ao sistema')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    papeis = models.ManyToManyField(
        'autenticacao.Papel',
        blank=True,
        related_name='usuarios'
    )

    permissoes_diretas = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='usuarios_diretos',
        help_text='Permissões específicas além das conferidas pelos papéis.'
    )

    allowed_filiais = models.ManyToManyField(
        'comum.Filial',
        blank=True,
        related_name='usuarios_com_acesso',
        help_text='Filiais que o usuário pode acessar.'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.first_name} ({self.username})'

    @property
    def nome_completo(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def delete(self, user=None):
        self.deleted_at = timezone.now()
        self.ativo = False
        self.save(update_fields=['deleted_at', 'ativo', 'updated_at'])