from turtle import up, update
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza a resposta do login para incluir dados do usuário.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        self.user.previous_login = self.user.last_login
        self.user.save(update_fields=['previous_login'])
        update_last_login(None, self.user)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'nome_completo': self.user.get_full_name(),
            'is_superuser': self.user.is_superuser,
            'is_staff': self.user.is_staff,
            'ultimo_login': str(self.user.previous_login),
            'permissoes': list(self.user.get_all_permissions()),
        }

        return data