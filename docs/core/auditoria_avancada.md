# Core — Auditoria Avançada

*(Este documento será detalhado em uma fase futura do projeto.)*

## 1. Visão Geral

O submódulo de **Auditoria Avançada** será responsável por registrar um log detalhado de todas as alterações de dados sensíveis no sistema. O objetivo é responder a três perguntas fundamentais para qualquer registro:

-   **Quem** fez a alteração? (`usuario`)
-   **Quando** foi feita? (`timestamp`)
-   **O que** foi alterado? (`dados_antes` e `dados_depois`)

## 2. Escopo da Auditoria

Serão auditadas, no mínimo, as seguintes operações:

-   Criação, atualização e exclusão (lógica) de todas as entidades principais.
-   Alterações em campos críticos (ex: CPF de uma `PessoaFisica`, CNPJ de uma `PessoaJuridica`, valor de um `Contrato`).
-   Mudanças de status (ex: `ativar`/`desativar` um `Cliente`).
-   Alterações de permissões e papéis de usuários.
-   Logins bem-sucedidos e tentativas de login falhas.
