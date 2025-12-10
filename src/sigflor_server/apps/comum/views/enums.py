from rest_framework.views import APIView
from rest_framework.response import Response
from ..registro_enums import buscar_todos_enums

class EnumsView(APIView):
    def get(self, request):
        return Response(buscar_todos_enums())
