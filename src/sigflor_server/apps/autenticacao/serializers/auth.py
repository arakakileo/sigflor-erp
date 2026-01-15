from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza a resposta do login para incluir dados do usuário.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'nome_completo': self.user.get_full_name(),
            'is_superuser': self.user.is_superuser,
            'is_staff': self.user.is_staff,
            'permissoes': list(self.user.get_all_permissions())
        }

        return data