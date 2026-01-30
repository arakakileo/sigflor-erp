# Projeto Sigflor — Status do MVP de RH

**Última Atualização:** 2026-01-26

---

## 1. Visão Geral do MVP

O MVP do Sigflor concentra-se no módulo de **Recursos Humanos** e suas dependências diretas, abrangendo:

- **Gestão Organizacional:** Estrutura multi-CNPJ, Clientes, Filiais
- **Cadastro Unificado de Pessoas:** PessoaFisica, PessoaJuridica
- **Admissão e Contratos:** Funcionários, Cargos, Documentos
- **Logística de Pessoal:** Projetos, Equipes
- **SST (Saúde Ocupacional):** ASOs, Exames
- **Alojamentos:** Gestão de moradias

### Fluxos de Negócio do MVP (docs/05_fluxos_de_negocio.md)
1. **5.1** Admissão de um Novo Funcionário
2. **5.2** Gestão de Dependentes
3. **5.3** Gestão de ASO (Atestado de Saúde Ocupacional)
4. **5.4** Alocação em Alojamento
5. **5.5** Criação e Gestão de Equipes
6. **5.6** Desligamento de Funcionário

---

## 2. Status de Implementação por Módulo

### Legenda
- ✅ **IMPLEMENTADO** — Modelo, Serializer, Service, View completos
- 🔄 **PARCIAL** — Modelo existe, mas faltam componentes
- ❌ **NÃO IMPLEMENTADO** — Precisa ser criado

---

### Módulo `comum` (Core)

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| PessoaFisica | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| PessoaJuridica | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Usuario | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Permissao/Papel | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Empresa | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cliente | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Filial | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Contrato | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Projeto | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Endereco + Vínculos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Contato + Vínculos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Documento + Vínculos | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Anexo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Deficiencia | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exame | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

### Módulo `rh` (Recursos Humanos)

### Normas e Padrões de Desenvolvimento (Atualizado 2026-01-27)
> [!IMPORTANT]
> **Services e Selectors:** TODOS os métodos de Services e Selectors DEVEM aceitar o parâmetro `user` (tipo `Usuario`).
> - Services: Para auditoria (`created_by`, `updated_by`).
> - Selectors: Para filtragem futura de permissões/filiais.

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Cargo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CargoDocumento | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Funcionario | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dependente | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Equipe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EquipeFuncionario | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Observações:**
- **Funcionario:** Refatorado e Integrado ao SST (Validação de Status).
- **Alocacao:** Domínio REMOVIDO do projeto e limpo do código.
- **Equipe:** Validado e completo.
- **CargoDocumento/Dependente:** Validados.

---

### Módulo `sst` (Saúde e Segurança do Trabalho)

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| CargoExame | ✅ | ✅ | —— | —— | —— | ✅ |
| ASO | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exame | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ExameRealizado | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| TipoEPI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EPI (Catálogo) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CargoEPI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Observação:**
- **Módulo SST Completo** (Aguardando apenas Migrations e Testes).
- Implementado fluxo automático de geração de solicitação e validação de pendências.
- **EPIs:** Implementado gestão completa de EPIs, catálogos (com CA) e vínculos por cargo (com validade de troca).

---

### Módulo `alojamento`

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Alojamento | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| AlojamentoFuncionario | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Observação:** O app `alojamento` não existe ainda.

---

## 3. Lista de Tarefas Priorizadas para Conclusão do MVP

### PRIORIDADE 1: Criar Módulo Alojamento

| # | Tarefa | Componentes a Criar | Esforço | Status |
|:-:|:-------|:--------------------|:-------:|:------:|
| 1.1 | Criar app Django `alojamento` | Estrutura inicial | Baixo | ⬜ |
| 1.2 | Implementar Alojamento e AlojamentoFuncionario | Models, Serializers, Services, Views | Alto | ⬜ |

### PRIORIDADE 2: Lógica de Negócio dos Fluxos Restantes

| # | Tarefa | Fluxo | Esforço | Status |
|:-:|:-------|:------|:-------:|:------:|
| 2.1 | Validar fluxo de gestão de ASO (Testes manuais) | Fluxo 5.3 | Alto | ⬜ |
| 2.2 | Validar fluxo de alojamento | Fluxo 5.4 | Médio | ⬜ |
| 2.3 | **Novo:** Validar fluxo de entrega de EPIs | - | Médio | ⬜ |

### PRIORIDADE 3: Qualidade e Infraestrutura

| # | Tarefa | Descrição | Esforço | Status |
|:-:|:-------|:----------|:-------:|:------:|
| 3.1 | Testes unitários para Services críticos (Funcionario, Equipe, ASO, EPI) | `tests/` | Alto | ⬜ |

---

## 4. Resumo Executivo

### O que está COMPLETO:
- ✅ Módulo `comum` (Core)
- ✅ Módulo `rh` (Completo)
- ✅ Módulo `sst` (Completo em código: ASO, Exames, EPIs)

### O que FALTA CRIAR:
- ❌ App `alojamento` completo.

### Estimativa de Esforço Restante:
- **Alojamento:** ~3 dias
- **Testes e Validação:** ~4 dias
- **Deploy/Migrations:** ~1 dia

**Total Estimado:** ~8 dias de desenvolvimento

---

## 5. Histórico de Alterações

| Data | Alteração |
| :--- | :--- |
| 2026-01-27 | **Refatoração CargoService:** Atualização do método `update` para utilizar métodos de Full Sync (`atualizar_*_cargo`). Garante exclusão de itens removidos das listas. |
| 2026-01-27 | **Refatoração Serviços Auxiliares de Cargo (Exame/EPI/Documento):** Implementação de métodos de sincronização (`atualizar_*_cargo`) para suporte a Full Sync no `CargoService`. Implementação de métodos de validação (`validar_*_funcionario`) em `ExameService` e `EPIService`. Padronização de Auditoria: `configurar_*` apenas define `created_by`, preservando `updated_by`. |
| 2026-01-27 | **Implementação Fluxo Entrega EPI (Task 2.3):** Criação de model `EntregaEPI`, service com cálculo de validade (baseado no Cargo) e API `/sst/entregas-epi/`. |
| 2026-01-27 | **Padronização de Auditoria e Validação:** Implementação de `save()` com `full_clean()` nos models de EPI. Refatoração de Services (EPI/ASO) para preenchimento automático de `created_by` e `updated_by` via parâmetro `user`. |
| 2026-01-27 | **Refatoração CargoEPI (SST):** Alteração da arquitetura de `CargoEPI` para aninhamento direto em `Cargo`. Remoção da API isolada `/sst/cargos-epis/` e centralização da gestão no `CargoService` via `EPIService`. |
| 2026-01-26 | **Implementação EPI (SST):** Criação dos domínios `TipoEPI`, `EPI` e `CargoEPI`. Implementação de Serializers, Services, Selectors e Views padronizadas (BaseRBACViewSet). Integração com `CargoSerializer` para exibir EPIs obrigatórios. |
| 2026-01-26 | **Implementação ASO (SST):** Implementação completa do ciclo de vida de ASO e Exames Realizados. Integração com RH para validação de ativação de funcionário. Refatoração de Enums. |
| 2026-01-26 | **Validação RH e SST Parcial (+ Refatoração Funcionario):** Correção do modelo `Funcionario` (remoção de Alocação). Validação completa dos domínios `Equipe` e `Exame`. |
| 2026-01-26 | **Atualização de Status (Pós-Auditoria Inicial):** Identificado remoção do domínio `Alocacao`. Identificado estado de `Equipe` e `SST`. |
| 2025-11-29 | **Reavaliação completa do status do projeto:** (Histórico anterior mantido). |
