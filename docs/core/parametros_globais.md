# Core — Parâmetros Globais

*(Este documento será detalhado em uma fase futura do projeto.)*

## 1. Visão Geral

O submódulo de **Parâmetros Globais** permitirá que administradores do sistema configurem e ajustem regras de negócio e comportamentos do ERP diretamente pela interface, sem a necessidade de intervenção técnica ou deploy de código.

## 2. Escopo dos Parâmetros

A plataforma permitirá a configuração de, no mínimo, os seguintes parâmetros:

-   **Validações de Upload:** Tamanho máximo e tipos de arquivo (`mimetype`) permitidos para os submódulos de **Documentos** e **Anexos**.
-   **Regras de Negócio:**
    -   Prazos padrão para vencimento de tarefas.
    -   Limites de aprovação para ordens de compra.
    -   Configurações de juros e mora para o módulo Financeiro.
-   **Integrações:**
    -   Credenciais e endpoints para APIs externas (ex: iFractal).
    -   Configurações de e-mail (SMTP) para notificações.
-   **Customização:**
    -   Valores padrão para campos de formulários.
    -   Formatos de numeração automática para entidades (ex: Matrícula de funcionário).
