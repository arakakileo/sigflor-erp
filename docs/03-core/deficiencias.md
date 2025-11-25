# Modulo Core — Deficiencias

## 1. Visao Geral

O submodulo **Deficiencias** permite registrar informacoes sobre deficiencias de pessoas fisicas no sistema.
E utilizado para:

- Controle de PCD (Pessoas com Deficiencia)
- Cumprimento de cotas legais
- Acompanhamento de saude ocupacional
- Relatorios de inclusao

Cada deficiencia e vinculada a uma **PessoaFisica**, permitindo que uma pessoa tenha multiplas deficiencias registradas.

---

## 2. Objetivo do Submodulo

- Registrar deficiencias de pessoas fisicas
- Classificar por tipo e grau
- Registrar CID (Classificacao Internacional de Doencas)
- Diferenciar entre congenitas e adquiridas
- Fornecer dados para relatorios de inclusao

---

## 3. Entidade: Deficiencia

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| pessoa_fisica | FK → PessoaFisica | Sim | Pessoa com a deficiencia |
| nome | varchar(200) | Sim | Nome/descricao da deficiencia |
| tipo | varchar(30) | Sim | Tipo da deficiencia |
| cid | varchar(20) | Nao | Codigo CID |
| grau | varchar(20) | Nao | Grau da deficiencia |
| data_diagnostico | date | Nao | Data do diagnostico |
| congenita | boolean | Sim (default=False) | Se e congenita |
| observacoes | text | Nao | Observacoes adicionais |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

### 3.2 Tipos de Deficiencia

| Tipo | Descricao |
|------|-----------|
| fisica | Deficiencia fisica |
| visual | Deficiencia visual |
| auditiva | Deficiencia auditiva |
| mental | Deficiencia mental |
| intelectual | Deficiencia intelectual |
| multipla | Deficiencia multipla |
| outra | Outras deficiencias |

### 3.3 Graus de Deficiencia

| Grau | Descricao |
|------|-----------|
| leve | Grau leve |
| moderado | Grau moderado |
| severo | Grau severo |
| profundo | Grau profundo |

---

## 4. Relacionamentos

- **N:1 com PessoaFisica**
  Cada deficiencia pertence a uma pessoa fisica.
  Uma pessoa pode ter multiplas deficiencias.

---

## 5. Regras de Negocio

1. Toda deficiencia deve estar vinculada a uma PessoaFisica valida.

2. Ao registrar uma deficiencia, o campo `possui_deficiencia` da PessoaFisica deve ser atualizado para `True`.

3. O CID e opcional mas recomendado para fins de relatorios.

4. Exclusao e sempre soft delete.

5. Uma pessoa pode ter multiplas deficiencias do mesmo tipo.

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| pessoa_nome | Nome completo da pessoa |

---

## 7. Endpoints (API)

### Base
`/api/comum/deficiencias/`

---

### 7.1 Listar

**GET** `/api/comum/deficiencias/`

Filtros possiveis:
- `search` - busca por nome, CID ou nome da pessoa
- `pessoa_fisica_id` - filtrar por pessoa
- `tipo` - filtrar por tipo
- `cid` - filtrar por CID

---

### 7.2 Obter por ID

**GET** `/api/comum/deficiencias/{id}/`

---

### 7.3 Criar Deficiencia

**POST** `/api/comum/deficiencias/`

```json
{
  "pessoa_fisica": "uuid-da-pessoa",
  "nome": "Paraplegia",
  "tipo": "fisica",
  "cid": "G82.2",
  "grau": "severo",
  "data_diagnostico": "2020-05-15",
  "congenita": false,
  "observacoes": "Resultado de acidente"
}
```

### 7.4 Editar Deficiencia

**PATCH** `/api/comum/deficiencias/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Por pessoa | GET | `/por_pessoa/?pessoa_fisica_id=uuid` | Lista deficiencias de uma pessoa |
| Pessoas com deficiencia | GET | `/pessoas_com_deficiencia/` | Lista pessoas que possuem deficiencia |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas gerais |

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/comum/deficiencias/{id}/`

---

## 8. Integracao com PessoaFisica

A PessoaFisica possui um campo booleano `possui_deficiencia`:

```python
class PessoaFisica(models.Model):
    possui_deficiencia = models.BooleanField(
        default=False,
        help_text='Indica se a pessoa possui alguma deficiencia'
    )
```

Este campo deve ser:
- Atualizado para `True` ao criar uma deficiencia
- Verificado ao remover todas as deficiencias de uma pessoa

---

## 9. Estatisticas Disponiveis

O endpoint `/estatisticas/` retorna:

```json
{
  "total_deficiencias": 45,
  "congenitas": 12,
  "adquiridas": 33,
  "por_tipo": [
    {"tipo": "fisica", "total": 20},
    {"tipo": "visual", "total": 15},
    {"tipo": "auditiva", "total": 10}
  ],
  "pessoas_com_deficiencia": 38
}
```

---

## 10. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | Pessoa fisica obrigatoria | Campo nao informado |
| 400 | Nome da deficiencia obrigatorio | Campo nao informado |
| 400 | Tipo invalido | Tipo nao reconhecido |
| 404 | Deficiencia nao encontrada | ID inexistente |
| 403 | Sem permissao | Usuario sem acesso |

---

## 11. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para pessoa_fisica, tipo e cid.
- Inline disponivel no admin de PessoaFisica.
