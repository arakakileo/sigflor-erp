from django.db import models

class Tipo(models.TextChoices):
    ADMISSIONAL = 'ADMISSIONAL', 'Admissional'
    PERIODICO = 'PERIODICO', 'Periódico'
    DEMISSIONAL = 'DEMISSIONAL', 'Demissional'
    RETORNO_AO_TRABALHO = 'RETORNO_AO_TRABALHO', 'Retorno ao Trabalho'
    MUDANCA_DE_FUNCAO = 'MUDANCA_DE_FUNCAO', 'Mudança de Função'

class Status(models.TextChoices):
    ABERTO = 'ABERTO', 'Aberto'
    EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
    FINALIZADO = 'FINALIZADO', 'Finalizado'
    CANCELADO = 'CANCELADO', 'Cancelado'

class Resultado(models.TextChoices):
    APTO = 'APTO', 'Apto'
    INAPTO = 'INAPTO', 'Inapto'
    APTO_COM_RESTRICOES = 'APTO_COM_RESTRICOES', 'Apto com Restrições'