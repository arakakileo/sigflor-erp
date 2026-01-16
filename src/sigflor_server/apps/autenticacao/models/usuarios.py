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
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    previous_login = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text='Data do login anterior ao atual'
    )
    
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='usuarios_criados'
    )

    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='usuarios_atualizados'
    )

    deleted_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='usuarios_deletados'
    )

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

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
        self.is_active = False
        if user is not None:
            self.deleted_by = user
        self.save(update_fields=['deleted_at', 'is_active', 'deleted_by', 'updated_at'])

    def restore(self, user=None):
        self.deleted_at = None
        self.is_active = True
        if user is not None:
            self.updated_by = user
            
        self.save(update_fields=['deleted_at', 'is_active', 'updated_by', 'updated_at'])