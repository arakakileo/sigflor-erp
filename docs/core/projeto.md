# Core — Projeto (Centro de Custo)

## 1. Visão Geral

A entidade **Projeto** é o **coração do controle de custos e da logística operacional** no Sigflor. Ela representa um "Centro de Custo" ou uma "Obra", sendo a entidade que conecta a estrutura comercial com a estrutura física da empresa.

O `Projeto` materializa o conceito do **"Tripé"** da operação, unindo:
1.  **Quem Paga:** O [Cliente](./cliente.md).
2.  **Quem Fatura:** A [Empresa](./empresa.md) do grupo.
3.  **Onde Executa:** A [Filial](./filial.md) (base operacional).

Esta entidade substitui o conceito anteriormente chamado de "SubContrato" e centraliza a alocação de todos os recursos (funcionários, equipamentos, etc.).

## 2. Estrutura da Entidade `Projeto`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `numero` | String | Código único, gerado automaticamente para identificação do projeto. |
| `descricao` | Text | Nome ou objeto do projeto (ex: "Manutenção da Fazenda X - Bloco Y"). |
| `cliente` | FK para `Cliente` | O cliente para quem o serviço está sendo prestado. |
| `empresa` | FK para `Empresa` | **(Automático)** A empresa do grupo que fatura. Preenchido com base na `empresa_gestora` do cliente. |
| `filial` | FK para `Filial` | A base operacional (alojamento, escritório) responsável pela execução. |
| `contrato` | FK para `Contrato` | (Opcional) O [Contrato](./contrato.md) comercial principal que ampara este projeto. |
| `data_inicio` | Date | Data de início das atividades do projeto. |
| `data_fim` | Date | (Opcional) Data de término prevista. |
| `status` | Enum | Status atual do projeto (`PLANEJADO`, `EM_EXECUCAO`, `CONCLUIDO`, `CANCELADO`). |

## 3. Regras de Negócio

1.  **Criação do Número:** O `numero` do projeto é gerado automaticamente pelo sistema no momento da criação e não pode ser alterado.
2.  **Preenchimento Automático da Empresa:** O campo `empresa` é **somente leitura** para o usuário. Seu valor é copiado do campo `empresa_gestora` do `Cliente` selecionado. Isso garante que o centro de custo esteja sempre alinhado com a estrutura de faturamento correta.
3.  **Vigência:** Um projeto é considerado ativo se seu `status` for `EM_EXECUCAO`.
3.  **Alocação de Recursos:** O `Projeto` é a entidade chave para a alocação de funcionários ([`hr.Funcionario`](../../hr/funcionarios.md)), veículos (módulo de Frota) e outros ativos.
5.  **Soft Delete:** Projetos seguem a política de exclusão lógica.

## 4. Endpoints da API

### Listar Projetos
`GET /api/core/projetos/`

Filtros: `status=EM_EXECUCAO`, `cliente_id=<uuid>`, `empresa_id=<uuid>`, `filial_id=<uuid>`

### Criar Projeto
`POST /api/core/projetos/`

**Request Body:**

```json
{
  "descricao": "Projeto de Silvicultura na Fazenda Boa Esperança",
  "cliente_id": "uuid-do-cliente",
  "filial_id": "uuid-da-filial-de-execucao",
  "contrato_id": "uuid-do-contrato-opcional",
  "data_inicio": "2025-02-01",
  "status": "PLANEJADO"
}
```
**Nota:** O `empresa_id` não é enviado, pois o backend o preencherá automaticamente.
