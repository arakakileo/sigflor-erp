# Arquitetura do Sistema — Sigflor

## 1. Visão Geral da Arquitetura

O Sigflor utiliza uma arquitetura moderna com **backend e frontend desacoplados**, o que garante escalabilidade, flexibilidade e facilidade de manutenção.

-   **Backend:** Construído com **Django** e **Django REST Framework (DRF)**, é responsável pela API, regras de negócio, persistência de dados e integrações externas.
-   **Frontend:** Desenvolvido em **React**, consome a API do backend e é responsável por toda a camada de apresentação e experiência do usuário.
-   **Comunicação:** A interação entre as duas camadas é feita exclusivamente via **API REST**, utilizando o padrão **JSON Web Token (JWT)** para autenticação e autorização.
-   **Banco de Dados:** **PostgreSQL**, pela sua robustez, performance e suporte a tipos de dados complexos.
-   **Infraestrutura:** O ambiente de desenvolvimento e produção é padronizado e orquestrado com **Docker**, simplificando o deploy e a escalabilidade.

---

## 2. Arquitetura do Backend: Padrão em Camadas

O backend adota uma arquitetura em camadas bem definida para garantir a separação de responsabilidades (SoC) e a testabilidade do código. O fluxo de uma requisição segue o padrão:

`Views -> Serializers -> Services -> Selectors -> Models`

-   **Views (ViewSets):** Coordenam o ciclo de `request/response`. Não contêm regras de negócio; sua função é orquestrar as chamadas para as camadas de serviço e de consulta.
-   **Serializers:** Validam, transformam e formatam os dados que entram e saem da API.
-   **Services:** **É aqui que residem todas as regras de negócio**. Casos de uso como "Admitir Funcionário", "Gerar Matrícula" ou "Alocar Colaborador em Projeto" são implementados nesta camada, tornando-os isolados e fáceis de testar.
-   **Selectors:** Centralizam e otimizam as consultas ao banco de dados. São responsáveis por queries complexas, utilizando `select_related` e `prefetch_related` para evitar problemas de N+1 e garantir a performance.
-   **Models:** Representam a estrutura de dados (ORM) e as constraints de integridade.

---

## 3. Decisões Arquiteturais Chave (ADRs)

Decisões importantes foram tomadas para garantir a integridade e a performance do sistema:

1.  **Soft Delete (Exclusão Lógica) Global:** Nenhum registro é fisicamente apagado. Todos os modelos herdam de uma classe base que implementa a exclusão lógica através de um campo `deleted_at`. Isso garante rastreabilidade total e facilita auditorias.
2.  **Veto a Chaves Estrangeiras Genéricas (GFK):** Para garantir a integridade referencial e a clareza do schema, o uso de GFKs (como o `ContentType Framework`) foi vetado em favor de tabelas de vínculo explícitas (ex: `PessoaFisicaEndereco`).
3.  **Centralização do "Projeto" no Core:** A entidade `Projeto` (que representa o **Centro de Custo**) foi movida para o módulo `core`, pois é uma entidade transversal, utilizada por RH, Financeiro e Estoque.
4.  **A Estrutura de "Tripé" para Centro de Custo:** Um `Projeto` é a entidade que une três pilares essenciais da operação:
    -   **Empresa:** O CNPJ do grupo que fatura.
    -   **Cliente:** Quem paga pelo serviço.
    -   **Filial:** Onde o serviço é executado (base logística).
5.  **Denormalização Controlada no Projeto:** Para otimizar queries, o `Projeto` armazena uma referência direta à `Empresa`, embora essa informação já exista no `Cliente`. O campo `empresa` é `read-only` e preenchido automaticamente via `save()`, garantindo consistência (`self.empresa = self.cliente.empresa_gestora`), performance e imutabilidade do histórico.

---

## 6. Sistema de Permissões (RBAC com Nível Regional/Setorial)

O sistema de permissões do Sigflor é baseado em RBAC (Role-Based Access Control) e estende-se para cobrir requisitos de acesso regional e setorial, além dos níveis de ação (visualizar/editar/baixar).

*   **RBAC Central (`Permissao` e `Papel`):**
    *   **`Permissao`:** Representa permissões atômicas com nomenclatura `modulo_entidade_acao` (ex: `rh_funcionario_visualizar`, `sst_aso_criar`, `comum_projeto_gerenciar`, `rh_relatorio_funcionario_baixar`).
    *   **`Papel`:** Agrupa `Permissao`s, e usuários podem ter múltiplos papéis.

*   **Permissões Setoriais e de Ação:** São intrínsecas à nomenclatura das `Permissao`s.

*   **Permissões Regionais (Controle de Acesso por Objeto/Contexto):**
    *   Para controle granular ("usuário só pode editar funcionários da Filial X"), o modelo `Usuario` (`comum.Usuario`) será estendido com um campo Many-to-Many (`allowed_filiais`) para `Filial`.
    *   As verificações de acesso regional serão implementadas **explicitamente na camada de `Services`**. Antes de qualquer operação (CRUD), o serviço verificará:
        1.  A `Permissao` genérica do usuário.
        2.  Se a entidade em questão (ex: `Funcionario`) pertence a uma `Filial` que o usuário tem acesso (via `usuario.allowed_filiais`).
    *   Esta abordagem evita a complexidade de bibliotecas de terceiros para permissões de objeto no MVP, mantendo o controle explícito e otimizado.

*   **Gestão de Superusuários:** Superusuários têm acesso total e gerenciam `Usuarios`, `Papeis` e `Permissões` via painel administrativo.

*   **Suporte Mobile:** As validações de permissão são feitas via API REST no backend, com autenticação JWT, sendo transparente para o frontend mobile.

---

## 4. Stack Tecnológica

| Componente          | Tecnologia Escolhida         |
| ------------------- | ---------------------------- |
| **Linguagem Backend** | Python 3.11+                 |
| **Framework Backend** | Django 5.x + DRF             |
| **Banco de Dados**    | PostgreSQL 15+               |
| **Frontend**        | React                        |
| **Infraestrutura**  | Docker                       |
| **Autenticação**    | JWT (SimpleJWT)              |
