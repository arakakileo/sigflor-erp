# Projeto Sigflor — Status do MVP de RH

**Última Atualização:** 2025-11-29

---

## 1. Visão Geral do MVP

O MVP do Sigflor concentra-se no módulo de **Recursos Humanos** e suas dependências diretas, abrangendo:

- **Gestão Organizacional:** Estrutura multi-CNPJ, Clientes, Filiais
- **Cadastro Unificado de Pessoas:** PessoaFisica, PessoaJuridica
- **Admissão e Contratos:** Funcionários, Cargos, Documentos
- **Logística de Pessoal:** Projetos, Alocações, Equipes
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

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Cargo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CargoDocumento | ✅ | ❌ | ❌ | ❌ | ❌ | 🔄 |
| Funcionario | ✅ | 🔄 | 🔄 | ✅ | ✅ | 🔄 |
| Dependente | ✅ | 🔄 | 🔄 | ✅ | ❌ | 🔄 |
| Equipe | ✅ | ❌ | ❌ | ❌ | ❌ | 🔄 |
| EquipeFuncionario | ✅ | ❌ | ❌ | ❌ | ❌ | 🔄 |
| Alocacao | ✅ | ❌ | ❌ | ❌ | ❌ | 🔄 |

**Observações:**
- Funcionario: Serializers e Services precisam atualização para refletir mudanças no modelo
- Dependente: Serializers e Services precisam atualização (agora usa PessoaFisica)
- CargoDocumento, Equipe, EquipeFuncionario, Alocacao: Apenas models criados

---

### Módulo `sst` (Saúde e Segurança do Trabalho)

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| CargoExame | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ASO | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| ExameRealizado | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Observação:** O app `sst` não existe ainda. Precisa ser criado.

---

### Módulo `alojamento`

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Alojamento | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| AlojamentoFuncionario | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Observação:** O app `alojamento` não existe ainda. Precisa ser criado.

---

## 3. Lista de Tarefas Priorizadas para Conclusão do MVP

### PRIORIDADE 1: Correções Urgentes (Modelos alterados recentemente)

Estas tarefas são necessárias porque os modelos foram refatorados e os componentes dependentes estão desatualizados.

| # | Tarefa | Componentes | Esforço |
|:-:|:-------|:------------|:-------:|
| 1.1 | Atualizar FuncionarioSerializer para refletir novos campos | `rh/serializers/funcionarios.py` | Baixo |
| 1.2 | Atualizar FuncionarioService para refletir novos campos | `rh/services/funcionarios.py` | Médio |
| 1.3 | Atualizar DependenteSerializer (agora usa PessoaFisica) | `rh/serializers/dependentes.py` | Médio |
| 1.4 | Atualizar DependenteService (agora usa PessoaFisica) | `rh/services/dependentes.py` | Médio |
| 1.5 | Atualizar CargoSerializer para incluir campos de risco e Nivel enum | `rh/serializers/cargos.py` | Baixo |
| 1.6 | Atualizar CargoService para incluir campos de risco | `rh/services/cargos.py` | Baixo |

---

### PRIORIDADE 2: Completar Módulo RH (Entidades com Model criado)

| # | Tarefa | Componentes a Criar | Esforço |
|:-:|:-------|:--------------------|:-------:|
| 2.1 | Implementar CargoDocumento completo | Serializer, Service, View, Selectors, URLs | Médio |
| 2.2 | Implementar Equipe completo | Serializer, Service, View, Selectors, URLs | Médio |
| 2.3 | Implementar EquipeFuncionario completo | Serializer, Service (integrado com Equipe) | Médio |
| 2.4 | Implementar Alocacao completo | Serializer, Service, View, Selectors, URLs | Médio |
| 2.5 | Criar selectors para Dependente | `rh/selectors/dependentes.py` | Baixo |

---

### PRIORIDADE 3: Criar Módulo SST (Saúde e Segurança)

Este módulo é **essencial para o Fluxo 5.3 (Gestão de ASO)**.

| # | Tarefa | Componentes a Criar | Esforço |
|:-:|:-------|:--------------------|:-------:|
| 3.1 | Criar app Django `sst` | `apps.py`, `__init__.py`, estrutura de pastas | Baixo |
| 3.2 | Criar model CargoExame | `sst/models/cargo_exame.py` | Baixo |
| 3.3 | Criar model ASO | `sst/models/aso.py` | Médio |
| 3.4 | Criar model ExameRealizado | `sst/models/exame_realizado.py` | Médio |
| 3.5 | Implementar CargoExame completo | Serializer, Service, View, Selectors | Médio |
| 3.6 | Implementar ASO completo | Serializer, Service (complexo), View | Alto |
| 3.7 | Implementar ExameRealizado completo | Serializer, Service, View | Médio |
| 3.8 | Registrar app `sst` em INSTALLED_APPS | `core/settings.py` | Baixo |
| 3.9 | Configurar URLs do módulo SST | `sst/urls.py`, `core/urls.py` | Baixo |

---

### PRIORIDADE 4: Criar Módulo Alojamento

Este módulo é **essencial para o Fluxo 5.4 (Alocação em Alojamento)**.

| # | Tarefa | Componentes a Criar | Esforço |
|:-:|:-------|:--------------------|:-------:|
| 4.1 | Criar app Django `alojamento` | `apps.py`, `__init__.py`, estrutura de pastas | Baixo |
| 4.2 | Criar model Alojamento | `alojamento/models/alojamentos.py` | Médio |
| 4.3 | Criar model AlojamentoFuncionario | `alojamento/models/alojamentos.py` | Médio |
| 4.4 | Implementar Alojamento completo | Serializer, Service, View, Selectors | Médio |
| 4.5 | Implementar AlojamentoFuncionario completo | Serializer, Service, View | Médio |
| 4.6 | Registrar app `alojamento` em INSTALLED_APPS | `core/settings.py` | Baixo |
| 4.7 | Configurar URLs do módulo Alojamento | `alojamento/urls.py`, `core/urls.py` | Baixo |

---

### PRIORIDADE 5: Lógica de Negócio dos Fluxos

Implementação das regras de negócio complexas descritas em `05_fluxos_de_negocio.md`.

| # | Tarefa | Fluxo | Esforço |
|:-:|:-------|:------|:-------:|
| 5.1 | Implementar lógica de admissão completa | Fluxo 5.1 | Alto |
| 5.2 | Implementar validação de documentos obrigatórios por cargo | Fluxo 5.1 | Médio |
| 5.3 | Implementar lógica de gestão de dependentes | Fluxo 5.2 | Médio |
| 5.4 | Implementar lógica de solicitação/finalização de ASO | Fluxo 5.3 | Alto |
| 5.5 | Implementar lógica de alocação em alojamento | Fluxo 5.4 | Médio |
| 5.6 | Implementar lógica de gestão de equipes | Fluxo 5.5 | Médio |
| 5.7 | Implementar lógica de desligamento de funcionário | Fluxo 5.6 | Alto |

---

### PRIORIDADE 6: Qualidade e Infraestrutura

| # | Tarefa | Descrição | Esforço |
|:-:|:-------|:----------|:-------:|
| 6.1 | Criar migrations para todos os modelos | `makemigrations` e revisão | Médio |
| 6.2 | Executar migrations | `migrate` | Baixo |
| 6.3 | Configurar admin para novos modelos | `admin.py` de cada app | Baixo |
| 6.4 | Escrever testes unitários para Services | `tests/` | Alto |
| 6.5 | Escrever testes de integração para Views | `tests/` | Alto |
| 6.6 | Integrar drf-spectacular para documentação OpenAPI | `settings.py`, `urls.py` | Médio |

---

## 4. Resumo Executivo

### O que está COMPLETO:
- ✅ Módulo `comum` (Core) — todas as entidades base
- ✅ Modelos do módulo `rh` — todos criados e alinhados com documentação

### O que está PARCIAL:
- 🔄 Serializers/Services/Views do `rh` — precisam atualização após refatoração dos models
- 🔄 Equipe, EquipeFuncionario, Alocacao, CargoDocumento — apenas models criados

### O que FALTA CRIAR:
- ❌ App `sst` completo (CargoExame, ASO, ExameRealizado)
- ❌ App `alojamento` completo (Alojamento, AlojamentoFuncionario)
- ❌ Lógica de negócio dos 6 fluxos principais

### Estimativa de Esforço Restante:
- **Prioridade 1 (Correções):** ~1-2 dias
- **Prioridade 2 (Completar RH):** ~2-3 dias
- **Prioridade 3 (SST):** ~3-4 dias
- **Prioridade 4 (Alojamento):** ~2-3 dias
- **Prioridade 5 (Lógica de Negócio):** ~4-5 dias
- **Prioridade 6 (Qualidade):** ~3-4 dias

**Total Estimado:** ~15-21 dias de desenvolvimento

---

## 5. Histórico de Alterações

| Data | Alteração | Arquivos Modificados |
| :--- | :--- | :--- |
| 2025-11-29 | **Refatoração do modelo `Documento`:** Remoção de GFK, adição de campos `nome_original`, `mimetype`, `tamanho`. Criação de tabelas de vínculo `PessoaFisicaDocumento` e `PessoaJuridicaDocumento` com campo `principal`. Atualização do enum `Tipo` conforme documentação. | `models/documentos.py`, `serializers/documentos.py`, `services/documentos.py`, `models/__init__.py`, `docs/core/documentos.md` |
| 2025-11-29 | **Refatoração do modelo `Endereco`:** Remoção de GFK, criação de tabelas de vínculo `PessoaFisicaEndereco`, `PessoaJuridicaEndereco` e `FilialEndereco` com campos `tipo` e `principal`. Atualização do enum `UF` com nomes completos. | `models/enderecos.py`, `serializers/enderecos.py`, `services/enderecos.py`, `models/__init__.py`, `docs/core/enderecos.md` |
| 2025-11-29 | **Refatoração do modelo `PessoaJuridica`:** Remoção de `GenericRelation` para endereços e documentos. Criação do enum `SituacaoCadastral`. Remoção de campos extras não documentados (`inscricao_municipal`, `porte`, `natureza_juridica`, `atividade_principal`, `atividades_secundarias`, `anexos`). Simplificação dos serializers e service. | `models/pessoa_juridica.py`, `serializers/pessoa_juridica.py`, `services/pessoa_juridica.py`, `models/__init__.py`, `serializers/__init__.py` |
| 2025-11-29 | **Refatoração do modelo `Projeto`:** Adição de campos `numero` (auto-gerado), `descricao`, `contrato`, `data_inicio`, `data_fim`, `status`. Criação do enum `StatusProjeto`. Renomeado campo `nome` para `descricao`. Implementação de geração automática de número no formato `PRJ-YYYYMM-NNNN`. Novos serializers e métodos no service. | `models/projeto.py`, `serializers/projeto.py`, `services/projeto.py`, `models/__init__.py`, `serializers/__init__.py`, `docs/core/projeto.md` |
| 2025-11-29 | **Remoção do modelo `SubContrato`:** Modelo removido pois não está na documentação. O conceito foi substituído pelo `Projeto` como centro de custo. Removidos: model, serializer, service, view, selectors, admin, urls. | Múltiplos arquivos em `comum/` |
| 2025-11-29 | **Verificação e alinhamento das tabelas de vínculo de PessoaJuridica:** Verificação de `PessoaJuridicaEndereco`, `PessoaJuridicaContato`, `PessoaJuridicaDocumento`. Correção do enum `Contato.Tipo` para usar valores uppercase (`CELULAR`, `FIXO`, `EMAIL`, `OUTRO`). Adição de `related_name` às FKs das tabelas de vínculo de contato. Adição de `contato_emergencia` em `PessoaFisicaContato`. Atualização completa da documentação `contatos.md` e `pessoa_juridica.md`. | `models/contatos.py`, `docs/core/contatos.md`, `docs/core/pessoa_juridica.md` |
| 2025-11-29 | **Refatoração completa dos modelos RH:** Alinhamento de todos os modelos do módulo RH com a documentação. | Múltiplos arquivos em `rh/models/` |
|  | • **Funcionario:** Removida referência a `SubContrato`. Adicionados campos `peso_corporal`, `altura`, `indicacao`, `cidade_atual`. Renomeados campos para padrão (`salario_nominal`, `conta_corrente`, `pis_pasep`, `chave_pix`, `gestor_imediato`, `tamanho_calcado`). Adicionado `TipoConta` enum. Todos os enums alterados para uppercase. Referência alterada de `EmpresaCNPJ` para `Empresa`. Removidos campos não documentados (`departamento`, `carga_horaria_semanal`, `horario_entrada`, `horario_saida`). | `rh/models/funcionarios.py` |
|  | • **Cargo:** Adicionados campos de risco ocupacional (`risco_fisico`, `risco_biologico`, `risco_quimico`, `risco_ergonomico`, `risco_acidente`). Criado enum `Nivel` com valores corretos. Renomeado `salario` para `salario_base`. | `rh/models/cargos.py` |
|  | • **Dependente:** Modelo refatorado para usar referência a `PessoaFisica` (OneToOneField) em vez de armazenar dados diretamente. Removidos campos duplicados. Renomeado `incluso_ir` para `dependencia_irrf`. Adicionado campo `ativo`. Enum `Parentesco` alterado para uppercase. | `rh/models/dependentes.py` |
|  | • **Equipe/EquipeFuncionario:** Adicionado campo `ativa`. `lider` alterado de ForeignKey para OneToOneField com `on_delete=PROTECT`. Enum `TipoEquipe` alterado para uppercase. Adicionado `db_table`. `on_delete` em EquipeFuncionario alterado para CASCADE. | `rh/models/equipes.py` |
|  | • **Alocacao:** Modelo criado (não existia). Campos: `funcionario`, `projeto`, `data_inicio`, `data_fim`, `observacoes`. Constraint de unicidade e validação de datas. | `rh/models/alocacoes.py` (novo) |
|  | • **CargoDocumento:** Modelo criado (não existia). Campos: `cargo`, `documento_tipo`, `obrigatorio`, `condicional`. Define documentos obrigatórios por cargo. | `rh/models/cargo_documento.py` (novo) |
| 2025-11-29 | **Reavaliação completa do status do projeto:** Criação de lista priorizada de tarefas para conclusão do MVP. Identificação de gaps entre documentação e implementação. | `PROJETO_SIGFLOR_MVP_RH_STATUS.md` |
