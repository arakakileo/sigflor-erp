# Core — Anexos

## 1. Visão Geral

O submódulo de **Anexos** oferece uma funcionalidade genérica para o upload e armazenamento de arquivos não estruturados, como imagens, fotos de campo, comprovantes auxiliares e outros documentos informais.

Diferente do submódulo de **Documentos**, que lida com arquivos formais e categorizados (RG, CNH, Contrato Social), os anexos são utilizados para registros complementares do dia a dia.

## 2. Estrutura da Entidade `Anexo`

| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id` | UUID | Chave primária. |
| `nome_original` | String | Nome do arquivo no momento do upload. |
| `arquivo` | FileField | O caminho para o arquivo armazenado. |
| `descricao` | Text | Observações adicionais sobre o anexo. |
| `tamanho` | Integer | Tamanho do arquivo em bytes. |
| `mimetype` | String | Tipo MIME do arquivo (ex: `image/jpeg`). |
| `content_type`| FK | (Uso de GFK é uma exceção aqui) A entidade à qual o anexo pertence. |
| `object_id` | UUID | (Uso de GFK) O ID da instância da entidade. |

**Nota sobre GFK:** Embora a arquitetura priorize tabelas de vínculo explícitas, o caso de uso para "anexos genéricos" é uma exceção comum onde o `GenericForeignKey` do Django pode ser aplicado para simplicidade.

## 3. Regras de Negócio

1.  **Validação de Arquivo:** O sistema valida o tipo (`mimetype`) e o tamanho máximo do arquivo no momento do upload, conforme definido nos parâmetros globais.
2.  **Armazenamento:** Os arquivos são salvos no storage padrão configurado no projeto (ex: S3, GCS, local).
3.  **Segurança:** O download de anexos requer autenticação e autorização, garantindo que apenas usuários permitidos acessem os arquivos.
4.  **Soft Delete:** Anexos seguem a política de exclusão lógica (`soft_delete`), preservando o histórico.

## 4. Endpoints da API

A gestão de anexos é geralmente realizada de forma aninhada dentro dos endpoints das entidades principais.

### Exemplo: Adicionar um anexo a um Funcionário

`POST /api/rh/funcionarios/{id}/anexos/`

**Request Body (multipart/form-data):**

-   `arquivo`: O arquivo a ser enviado.
-   `descricao`: "Foto tirada durante a inspeção de campo."

Isso proporciona uma API mais intuitiva e contextual, em vez de um endpoint genérico para todos os anexos do sistema.
