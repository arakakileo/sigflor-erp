# -*- coding: utf-8 -*-
from apps.comum.views.base import BaseRBACViewSet
from django.contrib.auth.models import Permission
from ..serializers import PermissaoSerializer
from .. import selectors

class PermissaoViewSet(BaseRBACViewSet):

    permissao_leitura = 'autenticacao.view_papel'
    permissao_escrita = 'autenticacao.change_papel'
    http_method_names = ['get', 'head', 'options']

    queryset = Permission.objects.all()
    serializer_class = PermissaoSerializer

    def get_queryset(self):
        return selectors.permissao_list(
            user=self.request.user,
            search=self.request.query_params.get('search')
        )