# Core — Cliente

## 1. Visão Geral

A entidade **Cliente** representa as empresas externas que contratam os serviços do grupo. Este é um cadastro corporativo central, essencial para os módulos de Contratos, Financeiro e Operações.

Um `Cliente` é uma especialização da entidade [Pessoa Jurídica](./pessoa_juridica.md), o que significa que ele herda todos os dados cadastrais (CNPJ, Razão Social) e relacionamentos (endereços, contatos) da `PessoaJuridica` base.

Esta entidade substitui o conceito anteriormente chamado de "Contratante".

## 2. Estrutura da Entidade `Cliente`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `pessoa_juridica` | FK (1:1) para `PessoaJuridica` | Os dados legais da empresa cliente. |
| `empresa_gestora` | FK para `Empresa` | **Campo Crítico.** Define qual [Empresa](./empresa.md) do grupo é a "dona da conta" e responsável pelo faturamento deste cliente. |
| `ativo` | Boolean | Indica se o cliente está ativo e pode ser selecionado em novos contratos. |
| `descricao` | Text | Observações internas sobre o cliente. |

## 3. Regras de Negócio

1.  **Base em Pessoa Jurídica:** Todo `Cliente` deve estar, obrigatoriamente, vinculado a uma `PessoaJuridica` única e válida.
2.  **Empresa Gestora Obrigatória:** O campo `empresa_gestora` é mandatório e define o vínculo comercial principal. Todos os [Projetos](./projeto.md) criados para este `Cliente` herdarão essa empresa para fins de faturamento e centro de custo.
3.  **Status de Ativação:** Um cliente `inativo` não pode ser usado em novos `Projetos` ou `Contratos`, mas seu histórico é preservado.
4.  **Soft Delete:** Clientes seguem a política de exclusão lógica.

## 4. Endpoints da API

### Listar Clientes
`GET /api/core/clientes/`

Filtros: `ativo=true`, `search=<razao_social/cnpj>`

### Criar Cliente
`POST /api/core/clientes/`

**Request Body:**

```json
{
  "pessoa_juridica": {
    "razao_social": "Cliente Exemplo S.A.",
    "nome_fantasia": "Cliente Exemplo",
    "cnpj": "11222333000144"
  },
  "empresa_gestora_id": "uuid-da-empresa-do-grupo",
  "ativo": true
}
```
O backend deve criar a `PessoaJuridica` e, em seguida, o `Cliente`, vinculando os dois.

### Atualizar Cliente
`PATCH /api/core/clientes/{id}/`

Permite alterar a descrição, o status `ativo` ou a `empresa_gestora`. A alteração dos dados da `PessoaJuridica` deve ser feita em seu próprio endpoint.
