# Progresso do Projeto Sigflor - MVP de RH

Este documento serve como um guia de progresso, registrando o estado atual do projeto, as decisões tomadas, as implementações concluídas e o que ainda precisa ser feito para o MVP (Produto Mínimo Viável) focado no módulo de Recursos Humanos.

## 1. Visão Geral do MVP

O MVP do Sigflor foca na estruturação do "chão de fábrica" do RH, garantindo a integridade dos dados para gestão de pessoal, alocação de custos por projeto e logística de funcionários. O objetivo é padronizar cadastros e processos para empresas de grande porte no setor de reflorestamento.

## 2. Decisões Arquiteturais Chave e Justificativas

As seguintes decisões arquiteturais foram tomadas para garantir a escalabilidade, manutenibilidade e robustez do sistema, alinhadas com Django, DRF e PostgreSQL:

*   **Arquitetura de Monólito Modular:** Adotada para balancear simplicidade de desenvolvimento/deploy com baixo acoplamento entre módulos, permitindo futuras extrações para microsserviços, se necessário.
*   **Padrão em Camadas (Views -> Serializers -> Services -> Selectors -> Models):** Garante a separação de responsabilidades (SoC) e melhora a testabilidade do código, concentrando regras de negócio na camada de `Services`.
*   **Soft Delete Global:** Implementado para todos os modelos via `SoftDeleteModel` (em `comum/models/base.py`), assegurando rastreabilidade total e auditoria, evitando a perda permanente de dados.
*   **Veto a Chaves Estrangeiras Genéricas (GFKs):** Decisão para manter a integridade referencial e clareza do schema do banco de dados, preferindo tabelas de vínculo explícitas.
*   **Centralização da Entidade `Projeto` no Módulo `comum`:** O `Projeto` foi definido como uma entidade transversal, representando o Centro de Custo/Obra, essencial para RH, Financeiro e Estoque. Sua localização no módulo `comum` facilita o acesso por outros apps.
*   **Estrutura de "Tripé" para `Projeto`:** Um `Projeto` é vinculado a uma `Empresa` (quem fatura), um `Cliente` (quem paga) e uma `Filial` (onde o serviço é executado). Isso garante uma visão completa da alocação de custos.
*   **Denormalização Controlada em `Projeto`:** O campo `empresa` no modelo `Projeto` é preenchido automaticamente a partir da `empresa_gestora` do `Cliente`. Isso otimiza consultas e garante a consistência e imutabilidade do histórico do projeto.
*   **Tratamento de Erros Consistente na API:** Implementado um handler de exceções customizado no DRF (`core/exceptions.py`) para garantir respostas de erro padronizadas, amigáveis, com status codes corretos e detalhes de validação por campo. Isso centraliza e otimiza o tratamento de erros da API. (POSITIVO)
*   **Sistema de Permissões (RBAC com Nível Regional/Setorial):** A arquitetura de permissões utiliza RBAC (`Permissao`, `Papel`). Para controle de acesso regional, o modelo `Usuario` (`comum.Usuario`) foi estendido com um campo Many-to-Many (`allowed_filiais`) para `Filial`. As verificações de permissão (genéricas e regionais) serão realizadas na camada de `Services`. Superusuários gerenciam usuários/papéis/permissões. A API REST com JWT suportará o app mobile. Esta decisão está documentada em `docs/02_arquitetura.md`.
    *   **Escopo do MVP para Permissões:** Para o MVP, focamos em:
        1.  **Extensão do Modelo `Usuario` com `allowed_filiais`:** Essencial para a base do controle regional.
        2.  **Verificações de Permissão *Genérica* (RBAC) nas `Views`:** Rejeitar requisições inválidas cedo.
        3.  **Estrutura para Verificações de Permissão *Regional* nos `Services`:** Garantir que `Services` possam receber contexto de usuário para futuras implementações granulares. A implementação completa pode ser faseada.
        **Pode esperar para depois do MVP:** Implementação completa para todos os módulos, UI de gestão de permissões no frontend, otimizações de caching pesado. (POSITIVO)
*   **Geração de Matrículas (Nova Decisão):**
    *   **MVP:** Matrículas serão **inseridas manualmente**, mas o campo `matricula` no modelo `Funcionario` manterá a restrição `unique=True` para garantir a integridade dos dados.
    *   **Futuro:** Uma função de geração dinâmica de matrícula (globalmente única e estruturada) será mantida **comentada** no código, com placeholders para a inclusão de um identificador de cliente/empresa, para ser ativada e formatada posteriormente. (POSITATIVO)

## 3. Progresso da Implementação de Modelos (MVP de RH)

### Módulo `comum` (Core/Entidades Centrais)

*   **`PessoaFisica`:** Modelo existente. (POSITIVO)
*   **`PessoaJuridica`:** Modelo existente. (POSITIVO)
*   **`Usuario`:** Modelo existente. (POSITIVO)
    *   **Campo Many-to-Many `allowed_filiais`:** **IMPLEMENTADO.** (POSITIVO)
*   **`Permissao` / `Papel` (RBAC):** Modelos existentes. (POSITIVO)
*   **`EmpresaCNPJ`:** Modelo existente. (POSITIVO)
*   **`Contratante` (Cliente):** Modelo existente. (POSITIVO)
*   **`Filial`:** Modelo existente. (POSITIVO)
*   **`Projeto` (Centro de Custo):** Modelo **criado** em `models/projeto.py` e importado em `__init__.py`. Inclui lógica de auto-preenchimento da `empresa`. (POSITIVO)
    *   **Serializadores (`serializers/projeto.py`), Serviços (`services/projeto.py`), Views (`views/projeto.py`) e URLs:** **IMPLEMENTADO.** (POSITIVO)
    *   **Seletores (`selectors/__init__.py`):** **IMPLEMENTADO.** (POSITIVO)
*   **`Endereco`:** Modelo existente. (POSITIVO)
*   **`Contato`:** Modelo existente. (POSITIVO)
*   **`Documento`:** Modelo existente. (POSITIVO)
*   **`Anexo`:** Modelo existente. (POSITIVO)
*   **`Deficiencia`:** Modelo existente. (POSITIVO)
*   **`Contrato` / `SubContrato`:** Modelos existentes. (POSITIVO)
*   **`Exame` (mestre):** Modelo **criado** em `models/exame.py` e importado em `__init__.py`. (POSITIVO)
    *   **Serializadores (`serializers/exame.py`), Serviços (`services/exame.py`), Views (`views/exame.py`) e URLs:** **IMPLEMENTADO.** (POSITIVO)
    *   **Seletores (`selectors/__init__.py`):** **IMPLEMENTADO.** (POSITIVO)

### Módulo `rh` (Recursos Humanos)

*   **`Funcionario`:** Modelo **atualizado** em `models/funcionarios.py` para incluir `ForeignKey` para `Projeto` e índice. (POSITIVO)
    *   **Serializadores:** `FuncionarioListSerializer` atualizado para incluir `projeto_nome`. `FuncionarioSerializer` atualizado para incluir `projeto`, `projeto_nome`, e `matricula` em `read_only_fields`. (POSITIVO)
    *   **Serviços:** `FuncionarioCreateSerializer` e `FuncionarioUpdateSerializer` (se existir) precisarão ter o `user` passado para os serviços correspondentes. `FuncionarioService` atualizado com método `_check_filial_access` e parâmetros `user` adicionados em `create`, `update`, `delete`, e outros métodos relevantes para permissão regional. (POSITIVO)
    *   **Seletores (`selectors/__init__.py`):** Atualizado para incluir `user` e filtragem regional em `funcionario_list`, `funcionario_detail` e outras funções relacionadas.
*   **`Cargo`:** Modelo existente. (POSITIVO)
*   **`CargoDocumento`:** **Falta criar** o modelo. (NEGATIVO)
*   **`Dependente`:** Modelo existente. (POSITIVO)
*   **`Equipe` / `EquipeFuncionario`:** Modelos **criados** em `models/equipes.py` e importados em `__init__.py`. `Equipe` inclui `ForeignKey` para `Projeto`. (POSITIVO)

### Módulo `sst` (Saúde e Segurança do Trabalho)

*   **App `sst`:** O diretório existe, mas os modelos essenciais para o MVP estão faltando.
*   **`ASO`:** **Falta criar** o modelo. (NEGATIVO)
*   **`CargoExame`:** **Falta criar** o modelo. (NEGATIVO)
*   **`ExameRealizado`:** **Falta criar** o modelo. (NEGATIVO)

### Módulo `alojamento`

*   **App `alojamento`:** **Falta criar** o app Django. (NEGATIVO)
*   **`Alojamento` / `AlojamentoFuncionario`:** **Falta criar** os modelos. (NEGATIVO)

## 4. Checklist de Próximas Tarefas (Priorizadas para o MVP de RH)

Esta lista se concentra em completar as funcionalidades-chave de RH e suas dependências diretas, conforme os fluxos de negócio (`05_fluxos_de_negocio.md`).

### Prioridade 1: Implementação Essencial de Modelos, Serializadores, Services e Views para `comum` e `rh`.

1.  **Módulo `comum`:**
    *   ~~**`Exame` (Entidade Mestra):** Criar `models/exame.py`, `serializers/exame.py`, `services/exame.py`, `views/exame.py` e adicionar ao `__init__.py` (e registrar URLs). (Concluído)~~ 
    *   ~~**`Projeto` (Centro de Custo):** Criar `serializers/projeto.py`, `services/projeto.py`, `views/projeto.py` e adicionar ao `__init__.py` (e registrar URLs). (Concluído)~~ 
    *   ~~**Implementar Seletores (`selectors`) para todas as entidades já existentes:** Criar os arquivos `selectors` para `PessoaFisica`, `PessoaJuridica`, `EmpresaCNPJ`, `Contratante`, `Filial`, `Contrato`, `SubContrato`, `Endereco`, `Contato`, `Documento`, `Anexo`, `Deficiencia`, `Usuario`, `Permissao`, `Papel`, `Projeto`, `Exame`. (Concluído)~~ 
    *   ~~**Implementar Validadores (`validators`) para entidades que precisam de validação de negócio:** Criar validadores específicos para `PessoaFisica` (CPF), `PessoaJuridica` (CNPJ), `Contato` (formato de telefone/e-mail), `Documento` (tipos de arquivo), conforme necessário pelos fluxos de negócio e requisitos de dados. (Concluído)~~ 

2.  **Módulo `rh`:**
    *   **`Funcionario`:**
        *   ~~Criar `selectors/funcionarios.py`. (Concluído)~~ 
        *   ~~Atualizar `serializers/funcionarios.py` para incluir `projeto`, `projeto_nome` e `matricula` em `read_only_fields`. (Concluído)~~ 
        *   **Atualizar `services/funcionarios.py`:** Incluir o parâmetro `user` nos métodos `create` e `update`, e a lógica de permissão regional. (CONCLUÍDO: `_check_filial_access` criado, parâmetros `user` adicionados e chamadas para `create`, `update`, `delete` e outros métodos de status/transferência foram feitos.)
        *   **Atualizar `views/funcionarios.py`:** Integrar `HasPermission` e garantir que o `user` seja passado para os serviços.
    *   **`CargoDocumento`:** Criar `models/cargo_documento.py`, `serializers/cargo_documento.py`, `services/cargo_documento.py`, `views/cargo_documento.py` e adicionar ao `__init__.py`. (Necessário para a validação de documentos obrigatórios na admissão, Fluxo 5.1).
    *   **`Dependente`:**
        *   Criar `selectors/dependentes.py`. 
        *   Atualizar `serializers/dependentes.py`, `services/dependentes.py`, `views/dependentes.py` para incluir a lógica do fluxo de **Gestão de Dependentes (5.2)**.
    *   **`Equipe` / `EquipeFuncionario`:**
        *   Criar `selectors/equipes.py`. 
        *   Criar `serializers/equipes.py`, `services/equipes.py`, `views/equipes.py` e adicionar ao `__init__.py`. (Essencial para o fluxo de **Criação e Gestão de Equipes (5.5)** e alocação de funcionários a projetos.)

### Prioridade 2: Módulos de Suporte ao RH (SST e Alojamento)

1.  **Módulo `sst`:**
    *   **`ASO`:** Implementar `models/aso.py`, `serializers/aso.py`, `services/aso.py`, `views/aso.py` e adicionar ao `__init__.py` do `sst/models`. (Para o fluxo de **Gestão de ASO (5.3)**).
    *   **`CargoExame`:** Implementar `models/cargo_exame.py`, `serializers/cargo_exame.py`, `services/cargo_exame.py`, `views/cargo_exame.py` e adicionar ao `__init__.py` do `sst/models`. (Dependência do ASO).
    *   **`ExameRealizado`:** Implementar `models/exame_realizado.py`, `serializers/exame_realizado.py`, `services/exame_realizado.py`, `views/exame_realizado.py` e adicionar ao `__init__.py` do `sst/models`. (Dependência do ASO).
    *   Criar `selectors` para os modelos de SST.

2.  **Módulo `alojamento`:**
    *   **Criar o app Django `alojamento`:** Criar a estrutura básica do app, incluindo `models/`, `serializers/`, `services/`, `views/` e `__init__.py`s.
    *   **`Alojamento` / `AlojamentoFuncionario`:** Implementar `models/alojamentos.py`, `serializers/alojamentos.py`, `services/alojamentos.py`, `views/alojamentos.py` e adicionar ao `__init__.py` do `alojamento/models`. (Para o fluxo de **Alocação em Alojamento (5.4)**).
    *   Criar `selectors` para os modelos de Alojamento.

### Prioridade 3: Funcionalidades Adicionais e Melhorias

1.  **`Funcionario`:** Implementar a lógica de **Desligamento de Funcionário (5.6)** no `FuncionarioService`, incluindo o encerramento de vínculos com alojamento e equipe.
2.  **Testes:** Escrever testes unitários e de integração para todas as funcionalidades implementadas (altamente recomendado para cada nova funcionalidade).
3.  **Documentação da API:** Integrar `drf-spectacular` para documentação automática da API (gera o OpenAPI spec).
4.  **Configurações de Produção:** Rever e ajustar `settings.py` para produção (segurança, logging, etc.).

---

**Próximas Tarefas (Permissões - MVP):**

1.  ~~**Módulo `comum` - `Usuario`:** Estender o modelo `comum.Usuario` para incluir o campo Many-to-Many `allowed_filiais` para `Filial`. (CONCLUÍDO)~~ 
2.  ~~**Módulo `comum` - Permissões DRF:** Criar classes de permissão customizadas no DRF (ex: `HasPermission`) para verificar permissões genéricas nas `Views`. (CONCLUÍDO)~~ 
3.  ~~**Módulo `comum` - `Services` (Estrutura de Permissões):** Atualizar métodos relevantes nos `Services` e `Selectors` para aceitar o `user` como parâmetro, preparando para a lógica de filtro regional. (CONCLUÍDO)~~ 

**Próximo Passo Sugerido:** Prosseguir com a próxima tarefa da Prioridade 1: **Módulo `rh` - `Funcionario`:** Atualizar `services/funcionarios.py` para:
    *   Incluir o parâmetro `user` nos métodos `create` e `update`.
    *   Implementar a lógica de permissão regional e de acesso nos métodos `create`, `update` e `delete` do `FuncionarioService`.
    *   Adicionar `user` para o método `create` do `FuncionarioCreateSerializer` e passá-lo para o `FuncionarioService.create`.
    *   Adicionar `user` ao método `update` do `FuncionarioSerializer` e passá-lo para o `FuncionarioService.update`.