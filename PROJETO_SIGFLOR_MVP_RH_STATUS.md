# Projeto Sigflor — Status do MVP e Guia Arquitetural

**Última Atualização:** 2026-02-02

> [!IMPORTANT]
> **GUIA PARA O ASSISTENTE (AI):** Este documento é a **Fonte da Verdade** sobre a arquitetura, padrões e status do projeto. Antes de iniciar qualquer feature, consulte este arquivo para garantir consistência.

---

## 1. Diretrizes Arquiteturais e Padrões (The "Sigflor Way")

O Sigflor segue uma arquitetura em camadas inspirada em DDD (Domain-Driven Design) adaptada para Django (Styleguide de HackSoftware).

### 1.1. Camadas da Aplicação

| Camada | Responsabilidade | Regra de Ouro |
| :--- | :--- | :--- |
| **Model** (`models/`) | Definição de dados e relacionamentos. | **Mínima lógica.** Apenas métodos `__str__` ou propriedades simples. **NUNCA** colocar regras de negócio complexas no `save()`. |
| **Selector** (`selectors/`) | Consultas de leitura (Queries). | **Retorna QuerySets ou Objetos.** Deve aceitar `user` para filtros de permissão. **NUNCA** faz alterações no banco (writes). |
| **Service** (`services/`) | Regras de Negócio e Casos de Uso. | **Lugar da Lógica.** Onde acontece a "mágica". Recebe dados validados, executa regras, chama outros services e salva no banco. Deve ser transacional (`@transaction.atomic`). |
| **Serializer** (`serializers/`) | Validação de Entrada e Formatação de Saída. | **Validação de Formato.** Garante que o JSON de entrada está correto. **NUNCA** chama Services ou faz lógica de negócio complexa. |
| **View** (`views/`) | Entrada HTTP e Orquestração. | **O Maestro.** Recebe a request, chama o Serializer para validar, chama o Service para executar, e devolve a Response. **NUNCA** contém lógica de negócio. |

### 1.2. Decisões de Design (ADRs - Architectural Decision Records)

#### ADR-001: Agregados e Unificação
*   **Decisão:** Domínios muito acoplados devem ser unificados em um único módulo/arquivo para coesão.
*   **Exemplo:** `Cargo`, `CargoDocumento` e `CargoEPI` ficam todos dentro de `apps/rh/*` sob o arquivo `cargos.py` (ou importados nele).
*   **Motivo:** Facilita a manutenção e evita dependências circulares.

#### ADR-002: Service Orchestration vs Serializer logic
*   **Decisão:** **Proibido** usar `create()` ou `update()` do Serializer para lógica complexa.
*   **Motivo:** Serializers são acoplados ao HTTP/interface. Services são agnósticos e testáveis. A View deve pegar os dados validados (`serializer.validated_data`) e passar para o Service.

#### ADR-003: Imports e Dependências
*   **Decisão:** Services nunca devem importar Views ou Serializers.
*   **Decisão:** Imports dentro de métodos (Lazy Imports) são permitidos APENAS para evitar Import Circular em casos extremos, mas a preferência é refatorar a estrutura.

#### ADR-004: Soft Delete
*   **Decisão:** Deleção lógica via campo `deleted_at`.
*   **Padrão:** Selectors devem filtrar `deleted_at__isnull=True` por padrão.

---

## 2. Status de Implementação por Módulo

### Legenda
- ✅ **IMPLEMENTADO** — Modelo, Serializer, Service, View completos
- 🔄 **PARCIAL** — Modelo existe, mas faltam componentes
- ❌ **NÃO IMPLEMENTADO** — Precisa ser criado

### Módulo `comum` (Core)
*Base do sistema. Contém entidades reutilizáveis.*

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| PessoaFisica/Juridica | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Usuario/Auth | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Configuração (Empresa/Filial) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Endereco/Contato/Documento | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exame (Catálogo) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Módulo `rh` (Recursos Humanos)
*Fote da verdade sobre contratos e estrutura.*

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Cargo (Agregado) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Funcionario | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dependente | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Equipe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Módulo `sst` (Saúde e Segurança)
*Dependente do RH. Gerencia riscos e conformidade.*

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| ASO / ExameRealizado | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| EPI / EntregaEPI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### Módulo `alojamento`
*Gestão de moradia.*

| Entidade | Model | Serializer | Service | View | Selectors | Status |
|:---------|:-----:|:----------:|:-------:|:----:|:---------:|:------:|
| Alojamento | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 3. Backlog e Próximos Passos

### PRIORIDADE 1: Criar Módulo Alojamento
*   [ ] 1.1 Criar app Django `alojamento`
*   [ ] 1.2 Implementar CRUD de Alojamento e AlojamentoFuncionario

### PRIORIDADE 2: Validação Integrada
*   [x] 2.1 Validar ASO (RH <-> SST)
*   [x] 2.3 Validar EPI
*   [ ] 2.2 Validar Alojamento

---

## 4. Histórico de Mudanças Relevantes (Changelog)

| Data | Alteração | Contexto |
| :--- | :--- | :--- |
| **2026-02-02** | **Refatoração Cargo (Unificação)** | Unificação de CargoDocumento dentro de Cargo para alta coesão. Remoção de arquivos dispersos. |
| **2026-02-02** | **Conclusão SST** | Implementação final de EPIs e ASOs. |
| **2026-01-27** | **Padrão de Auditoria** | Injeção de `user` em todos os Services para rastreabilidade. |
| **2026-02-02** | **Fluxo de Contratação** | Implementação do "Draft Mode" (Aguardando Admissão) e endpoint `contratar`. Validação rígida de ASO/Docs/EPIs na ativação. |
