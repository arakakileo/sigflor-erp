# Core — Deficiências

## 1. Visão Geral

O submódulo de **Deficiências** permite o registro de informações sobre deficiências de [Pessoas Físicas](./pessoa_fisica.md), atendendo a requisitos legais (cotas para PCD), de saúde ocupacional e de inclusão.

O sistema permite que uma única pessoa tenha múltiplas deficiências registradas.

## 2. Estrutura da Entidade `Deficiencia`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `pessoa_fisica` | FK para `PessoaFisica` | A pessoa a quem a deficiência está associada. |
| `nome` | String | Nome ou breve descrição da deficiência (ex: "Hipoacusia"). |
| `tipo` | Enum | Tipo da deficiência (`FISICA`, `VISUAL`, `AUDITIVA`, `MENTAL`, `INTELECTUAL`, `MULTIPLA`). |
| `cid` | String | (Opcional) Código da Classificação Internacional de Doenças (CID). |
| `grau` | Enum | (Opcional) Grau da deficiência (`LEVE`, `MODERADO`, `SEVERO`). |
| `congenita` | Boolean | Indica se a deficiência é congênita. |
| `observacoes` | Text | Informações adicionais relevantes. |

## 3. Regras de Negócio

1.  **Vínculo com Pessoa Física:** Toda deficiência deve, obrigatoriamente, estar vinculada a uma `PessoaFisica`.
2.  **Sinalizador em Pessoa Física:** O cadastro de `PessoaFisica` possui um campo booleano `possui_deficiencia`. Este campo deve ser automaticamente atualizado para `True` quando a primeira deficiência for registrada e para `False` se todas as deficiências forem removidas.
3.  **Soft Delete:** Deficiências seguem a política de exclusão lógica.

## 4. Endpoints da API

A gestão de deficiências é realizada de forma aninhada, no contexto de uma `PessoaFisica`.

### Listar Deficiências de uma Pessoa
`GET /api/core/pessoas-fisicas/{id}/deficiencias/`

### Adicionar Deficiência a uma Pessoa
`POST /api/core/pessoas-fisicas/{id}/deficiencias/`

**Request Body:**

```json
{
  "nome": "Surdez Unilateral",
  "tipo": "AUDITIVA",
  "cid": "H90.4",
  "grau": "MODERADO",
  "congenita": false
}
```
