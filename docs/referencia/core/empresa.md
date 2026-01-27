# Core — Empresa

## 1. Visão Geral

A entidade **Empresa** representa cada um dos **CNPJs pertencentes ao próprio grupo econômico**. É o cadastro de "quem fatura", ou seja, as entidades legais que prestam os serviços e emitem as notas fiscais.

Assim como o [Cliente](./cliente.md), a `Empresa` é uma especialização da entidade [Pessoa Jurídica](./pessoa_juridica.md), centralizando os dados cadastrais básicos.

Esta entidade substitui o conceito anteriormente chamado de "EmpresaCNPJ".

## 2. Estrutura da Entidade `Empresa`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `pessoa_juridica` | FK (1:1) para `PessoaJuridica` | Os dados legais (CNPJ, Razão Social) da empresa do grupo. |
| `ativa` | Boolean | Indica se a empresa está operacional e pode ser usada em novos `Clientes` ou `Projetos`. |
| `descricao` | Text | (Opcional) Observações internas. |

## 3. Regras de Negócio

1.  **Base em Pessoa Jurídica:** Toda `Empresa` deve estar vinculada a uma `PessoaJuridica` única.
2.  **Status de Ativação:** Uma empresa `inativa` não pode ser selecionada como `empresa_gestora` de novos `Clientes`, mas seu histórico em registros existentes é mantido.
3.  **Soft Delete:** Empresas seguem a política de exclusão lógica.

## 4. Endpoints da API

### Listar Empresas
`GET /api/core/empresas/`

Filtros: `ativo=true`, `search=<razao_social/cnpj>`

### Criar Empresa
`POST /api/core/empresas/`

**Request Body:**

```json
{
  "pessoa_juridica": {
    "razao_social": "Sigflor Serviços Florestais LTDA",
    "nome_fantasia": "Sigflor",
    "cnpj": "44555666000177"
  },
  "ativa": true
}
```
O backend deve criar a `PessoaJuridica` e, em seguida, a `Empresa`, realizando o vínculo.

### Atualizar Empresa
`PATCH /api/core/empresas/{id}/`

Permite alterar a `descricao` e o status `ativo`. A alteração dos dados da `PessoaJuridica` (como a razão social) deve ser feita em seu próprio endpoint para garantir a auditoria.
