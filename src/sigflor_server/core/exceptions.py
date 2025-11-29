from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Handler de exceções customizado para a API do DRF.
    Garante respostas de erro padronizadas e amigáveis.
    """

    # Chama o handler padrão do DRF para obter a resposta inicial.
    response = exception_handler(exc, context)

    if response is not None:
        # Se for um erro de validação (400 Bad Request)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # A resposta padrão do DRF já vem com os detalhes por campo,
            # apenas ajustamos a estrutura da mensagem principal, se necessário.
            detail_message = "Verifique os dados informados." 
            field_errors = response.data
            
            response.data = {
                'detail': detail_message,
                'field_errors': field_errors
            }
        
        # Para outros erros tratados pelo DRF (ex: 404 Not Found, 403 Forbidden)
        elif isinstance(response.data, dict) and 'detail' in response.data:
            # Simplifica a mensagem de detalhe, se for o caso
            response.data = {
                'detail': str(response.data['detail'])
            }
        elif isinstance(response.data, list) and response.data: # Ex: lista de strings de erro
            response.data = {
                'detail': ", ".join(response.data)
            }
        else:
            # Para casos genéricos que o DRF tratou, mas sem 'detail' claro
            response.data = {
                'detail': 'Ocorreu um erro inesperado.'
            }
        
    else:
        # Para exceções não tratadas pelo DRF (erros 500 internos)
        # Nestes casos, `exc` é a exceção original.
        # Logar o erro completo aqui seria crucial.
        print(f"Erro interno do servidor: {exc}") # Substituir por um sistema de logging real

        response = Response(
            {'detail': 'Ocorreu um erro interno no servidor. Por favor, tente novamente mais tarde.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
