# Core — Soft Delete (Exclusão Lógica)

## 1. Visão Geral

O **Soft Delete** é um padrão de projeto implementado em todo o sistema Sigflor para garantir que os registros **nunca sejam permanentemente removidos** do banco de dados. Em vez de executar uma operação `DELETE`, o sistema atualiza um campo no registro para marcá-lo como "excluído".

Essa abordagem é fundamental para:

-   **Rastreabilidade e Histórico:** Manter um histórico completo de todos os dados que já existiram.
-   **Auditoria:** Permitir a auditoria de quem e quando um registro foi excluído.
-   **Segurança:** Prevenir a perda de dados por exclusão acidental.
-   **Integridade Referencial:** Manter a validade de chaves estrangeiras que apontam para registros "excluídos".

## 2. Implementação Técnica

A exclusão lógica é implementada através de uma classe de modelo abstrata (`ModeloBase` ou `SoftDeleteModel`), da qual a maioria das entidades do sistema herda.

### 2.1. Campos Adicionais no Modelo

Esta classe base adiciona, no mínimo, os seguintes campos a todas as tabelas:

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `created_at` | DateTime | Data e hora da criação do registro (autogerado). |
| `updated_at` | DateTime | Data e hora da última atualização (autogerado). |
| `deleted_at` | DateTime | **O campo chave.** Se for `NULL`, o registro está ativo. Se tiver uma data/hora, o registro está "excluído". |
| `deleted_by` | FK para `Usuario`| (Opcional) Armazena quem foi o usuário que solicitou a exclusão. |

### 2.2. Manager e QuerySet Customizados

Para que o Soft Delete funcione de forma transparente, o Django ORM é customizado:

-   **Manager Padrão (`objects`):** É sobrescrito para filtrar automaticamente apenas os registros onde `deleted_at IS NULL`. Assim, o código da aplicação (`Model.objects.all()`) nunca retorna registros excluídos por padrão.
-   **Manager Secundário (`all_objects`):** Um segundo manager é disponibilizado para permitir que consultas específicas (como relatórios administrativos) acessem *todos* os registros, incluindo os excluídos.
-   **Método `.delete()`:** O método é sobrescrito para executar um `UPDATE` (preenchendo `deleted_at`) em vez de um `DELETE` do SQL.

## 3. Implicações na API

Quando um usuário envia uma requisição `DELETE` para um endpoint, por exemplo:

`DELETE /api/rh/funcionarios/{id}/`

O sistema não apaga o funcionário. Ele apenas marca o registro correspondente com a data e hora da exclusão. Para o usuário, o efeito é o mesmo: o funcionário desaparece das listagens e telas. No entanto, o dado continua existindo no banco de dados para fins históricos e de auditoria.
