# Modulo Core — SubContratos

## 1. Visao Geral

O submodulo **SubContratos** representa a alocacao de recursos e custos em uma filial especifica, vinculada a um contrato principal.
E a **entidade central** para:

- Alocacao de funcionarios
- Controle de custos operacionais
- Gestao de patrimonios
- Rastreabilidade de operacoes por filial/contrato

O SubContrato e o ponto de conexao entre a estrutura organizacional (Filial) e a estrutura comercial (Contrato).

---

## 2. Objetivo do Submodulo

- Segmentar contratos por filial/unidade operacional
- Permitir alocacao precisa de funcionarios
- Centralizar custos por centro de custo
- Controlar vigencia por subcontrato
- Fornecer rastreabilidade completa de operacoes

---

## 3. Entidade: SubContrato

### 3.1 Estrutura da Tabela

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | UUID | Sim | Identificador unico |
| numero | varchar(20) | Sim (unique) | Numero auto-gerado (SC + 8 chars) |
| filial | FK → Filial | Sim | Filial do subcontrato |
| contrato | FK → Contrato | Sim | Contrato principal |
| descricao | text | Nao | Descricao do subcontrato |
| data_inicio | date | Sim | Data de inicio da vigencia |
| data_fim | date | Nao | Data de fim da vigencia |
| ativo | boolean | Sim (default=True) | Status do subcontrato |
| observacoes | text | Nao | Observacoes adicionais |
| created_at | datetime | Sim | Auditoria |
| updated_at | datetime | Sim | Auditoria |
| deleted_at | datetime | Nao | Soft delete |

### 3.2 Geracao do Numero

O numero e gerado automaticamente no formato:
- Prefixo: `SC`
- Sufixo: 8 caracteres alfanumericos aleatorios (A-Z, 0-9)
- Exemplo: `SC7X4K2M9P`

---

## 4. Relacionamentos

- **N:1 com Filial**
  Cada subcontrato pertence a uma filial.

- **N:1 com Contrato**
  Cada subcontrato pertence a um contrato principal.

- **1:N com Funcionario**
  Um subcontrato pode ter varios funcionarios alocados.

---

## 5. Regras de Negocio

1. O numero e gerado automaticamente e nao pode ser alterado.

2. Um subcontrato e considerado **vigente** quando:
   - ativo = True
   - data_inicio <= hoje
   - data_fim >= hoje OU data_fim e nulo

3. Exclusao e sempre soft delete.

4. Ao desativar um subcontrato, funcionarios alocados nao sao afetados.

5. Um subcontrato pode ser transferido para outra filial mantendo o mesmo numero.

6. O subcontrato herda informacoes do contrato (contratante, empresa).

---

## 6. Propriedades Calculadas

| Propriedade | Descricao |
|-------------|-----------|
| is_vigente | Retorna True se ativo e dentro do periodo |
| filial_nome | Nome da filial |
| contrato_numero | Numero interno do contrato |
| contratante_nome | Razao social do contratante (via contrato) |
| empresa_nome | Razao social da empresa (via contrato) |

---

## 7. Endpoints (API)

### Base
`/api/comum/subcontratos/`

---

### 7.1 Listar

**GET** `/api/comum/subcontratos/`

Filtros possiveis:
- `search` - busca por numero, filial ou contrato
- `ativo` - true/false
- `vigente` - true/false
- `filial_id` - filtrar por filial
- `contrato_id` - filtrar por contrato

---

### 7.2 Obter por ID

**GET** `/api/comum/subcontratos/{id}/`

---

### 7.3 Criar SubContrato

**POST** `/api/comum/subcontratos/`

```json
{
  "filial": "uuid-da-filial",
  "contrato": "uuid-do-contrato",
  "descricao": "SubContrato para operacoes norte",
  "data_inicio": "2024-01-01",
  "data_fim": "2024-12-31"
}
```

O numero sera gerado automaticamente.

### 7.4 Editar SubContrato

**PATCH** `/api/comum/subcontratos/{id}/`

### 7.5 Acoes Especiais

| Acao | Metodo | Endpoint | Descricao |
|------|--------|----------|-----------|
| Ativar | POST | `/{id}/ativar/` | Ativa o subcontrato |
| Desativar | POST | `/{id}/desativar/` | Desativa o subcontrato |
| Transferir filial | POST | `/{id}/transferir_filial/` | Move para outra filial |
| Listar vigentes | GET | `/vigentes/` | Lista subcontratos vigentes |
| Estatisticas | GET | `/estatisticas/` | Retorna estatisticas gerais |

**Transferir filial payload:**
```json
{
  "filial_id": "uuid-nova-filial"
}
```

### 7.6 Excluir (Soft Delete)

**DELETE** `/api/comum/subcontratos/{id}/`

---

## 8. Integracao com Funcionarios

O SubContrato e o campo de referencia para alocacao de funcionarios:

```python
class Funcionario(models.Model):
    subcontrato = models.ForeignKey(
        'comum.SubContrato',
        on_delete=models.PROTECT,
        related_name='funcionarios'
    )
```

Isso permite:
- Saber onde cada funcionario esta alocado
- Calcular custos por subcontrato
- Rastrear operacoes por filial/contrato
- Gerar relatorios por centro de custo

---

## 9. Erros e Excecoes

| Codigo | Mensagem | Motivo |
|--------|----------|--------|
| 400 | Filial obrigatoria | Campo nao informado |
| 400 | Contrato obrigatorio | Campo nao informado |
| 400 | ID da nova filial obrigatorio | Transferencia invalida |
| 404 | SubContrato nao encontrado | ID inexistente |
| 404 | Filial de destino nao encontrada | Transferencia invalida |
| 403 | Sem permissao | Usuario sem acesso |

---

## 10. Observacoes Tecnicas

- A PK e UUID e o soft delete e obrigatorio.
- Numero gerado com secrets.choice para seguranca.
- Service layer deve ser usada para criacao e edicao.
- Indices criados para numero, ativo, data_inicio, filial e contrato.
- O subcontrato utiliza on_delete=PROTECT para preservar integridade.
