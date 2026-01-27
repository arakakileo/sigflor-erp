# Core — Endereços (Especificação Detalhada)

## 1. Visão Geral

A entidade **Endereço** é um repositório centralizado para informações de localização. Ela é uma entidade genérica, projetada para ser reutilizada por qualquer outro modelo do sistema através de **tabelas de vínculo explícitas** (sem uso de Generic Foreign Keys).

**Propósito Arquitetural:** Garantir um formato padronizado para endereços, centralizar a lógica de validação e normalização, e evitar a repetição de campos de endereço em múltiplas tabelas.

**Status:** ✅ IMPLEMENTADO

---

## 2. Estrutura do Modelo (`comum.Endereco`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **logradouro** | `models.CharField` | `VARCHAR(255)` | `null=False`, `blank=False`. |
| **numero** | `models.CharField` | `VARCHAR(20)` | `null=True`, `blank=True`. |
| **complemento** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **bairro** | `models.CharField` | `VARCHAR(100)` | `null=True`, `blank=True`. |
| **cidade** | `models.CharField` | `VARCHAR(100)` | `null=False`, `blank=False`. |
| **estado** | `models.CharField` | `VARCHAR(2)` | `choices=Endereco.UF.choices` (Enum com UFs do Brasil). `null=False`, `blank=False`. |
| **cep** | `models.CharField` | `VARCHAR(8)` | `null=False`, `blank=False`. **Regra:** Armazenado sem máscara, apenas dígitos. |
| **pais** | `models.CharField` | `VARCHAR(50)` | `default='Brasil'`. |

### Campos Herdados (SoftDeleteModel)
- `created_at`, `updated_at`, `deleted_at`
- `created_by`, `updated_by`

### Propriedades Computadas
- **`cep_formatado`**: Retorna o CEP com máscara (ex: `12345-678`).
- **`endereco_completo`**: Retorna o endereço formatado em uma linha.

### Enum `UF` (Estados do Brasil)
```python
class UF(models.TextChoices):
    AC = 'AC', 'Acre'
    AL = 'AL', 'Alagoas'
    # ... todos os 27 estados
    TO = 'TO', 'Tocantins'
```

---

## 3. Tipos de Endereço (`TipoEndereco`)

```python
class TipoEndereco(models.TextChoices):
    RESIDENCIAL = 'RESIDENCIAL', 'Residencial'
    COMERCIAL = 'COMERCIAL', 'Comercial'
    CORRESPONDENCIA = 'CORRESPONDENCIA', 'Correspondência'
    OUTRO = 'OUTRO', 'Outro'
```

---

## 4. Relacionamentos (Modelo de Composição)

O modelo `Endereco` não possui vínculo direto com entidades. A associação é feita através de **tabelas de vínculo explícitas**.

### 4.1 Tabela de Vínculo: `PessoaFisicaEndereco`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`, `related_name='enderecos_vinculados'`. |
| **endereco** | `models.ForeignKey` para `Endereco` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_fisica'`. |
| **tipo** | `models.CharField` | `choices=TipoEndereco.choices`, `default='RESIDENCIAL'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Constraints:**
- `UniqueConstraint(fields=['pessoa_fisica', 'endereco'])` - Impede duplicação de vínculo.
- `UniqueConstraint(fields=['pessoa_fisica', 'tipo'], condition=principal=True)` - Apenas um endereço principal por tipo.

**Tabela PostgreSQL:** `pessoas_fisicas_enderecos`

### 4.2 Tabela de Vínculo: `PessoaJuridicaEndereco`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_juridica** | `models.ForeignKey` para `PessoaJuridica` | `on_delete=models.CASCADE`, `related_name='enderecos_vinculados'`. |
| **endereco** | `models.ForeignKey` para `Endereco` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_juridica'`. |
| **tipo** | `models.CharField` | `choices=TipoEndereco.choices`, `default='COMERCIAL'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Tabela PostgreSQL:** `pessoas_juridicas_enderecos`

### 4.3 Tabela de Vínculo: `FilialEndereco`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **filial** | `models.ForeignKey` para `Filial` | `on_delete=models.CASCADE`, `related_name='enderecos_vinculados'`. |
| **endereco** | `models.ForeignKey` para `Endereco` | `on_delete=models.CASCADE`, `related_name='vinculos_filial'`. |
| **tipo** | `models.CharField` | `choices=TipoEndereco.choices`, `default='COMERCIAL'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Tabela PostgreSQL:** `filiais_enderecos`

### Sobre os Campos `tipo` e `principal`

Os campos `tipo` e `principal` vivem nas tabelas de vínculo porque descrevem a **relação** entre a entidade e o endereço, não o endereço em si:
- Uma pessoa pode ter um endereço residencial e um comercial
- Pode ter múltiplos endereços do mesmo tipo (ex: dois comerciais), mas apenas um é o "principal"
- A constraint de unicidade garante apenas um endereço principal por tipo por entidade

---

## 5. Estratégia de Indexação

| Índice | Campos | Propósito |
| :--- | :--- | :--- |
| B-Tree | `cep` | Buscas rápidas por CEP |
| Composto | `(cidade, estado)` | Busca de endereços por localidade |

---

## 6. Camada de Serviço (`EnderecoService`)

### Métodos de Criação

- **`create(*, logradouro, cidade, estado, cep, ...)`**:
  - Cria um endereço sem vínculo com entidade.

- **`add_endereco_to_pessoa_fisica(*, pessoa_fisica, logradouro, cidade, estado, cep, tipo, principal, ...)`**:
  - Cria o endereço e o vínculo com `PessoaFisica` em uma transação.
  - Se `principal=True`, desmarca outros endereços do mesmo tipo como principal.
  - Retorna a instância de `PessoaFisicaEndereco`.

- **`add_endereco_to_pessoa_juridica(*, pessoa_juridica, ...)`**: Análogo ao acima.
- **`add_endereco_to_filial(*, filial, ...)`**: Análogo ao acima.

### Métodos de Atualização

- **`update(endereco, updated_by, **kwargs)`**: Atualiza dados do endereço.
- **`set_principal_pessoa_fisica(*, vinculo, updated_by)`**: Define como principal.
- **`set_principal_pessoa_juridica(*, vinculo, updated_by)`**: Análogo.
- **`set_principal_filial(*, vinculo, updated_by)`**: Análogo.

### Métodos de Exclusão

- **`delete(endereco, user)`**: Soft delete do endereço e todos os seus vínculos.
- **`remove_vinculo_pessoa_fisica(vinculo, user)`**: Remove apenas o vínculo.
- **`remove_vinculo_pessoa_juridica(vinculo, user)`**: Análogo.
- **`remove_vinculo_filial(vinculo, user)`**: Análogo.

### Métodos de Consulta

- **`get_enderecos_pessoa_fisica(pessoa_fisica)`**: Retorna todos os endereços vinculados.
- **`get_enderecos_pessoa_juridica(pessoa_juridica)`**: Análogo.
- **`get_enderecos_filial(filial)`**: Análogo.
- **`get_endereco_principal_pessoa_fisica(pessoa_fisica, tipo=None)`**: Retorna o endereço principal.
- **`get_endereco_principal_pessoa_juridica(pessoa_juridica, tipo=None)`**: Análogo.
- **`get_endereco_principal_filial(filial, tipo=None)`**: Análogo.

---

## 7. Serializers

| Serializer | Propósito |
| :--- | :--- |
| `EnderecoSerializer` | Leitura completa do endereço |
| `EnderecoCreateSerializer` | Criação com dados de vínculo |
| `PessoaFisicaEnderecoSerializer` | Vínculo PF com endereço aninhado |
| `PessoaFisicaEnderecoListSerializer` | Listagem simplificada |
| `PessoaJuridicaEnderecoSerializer` | Vínculo PJ com endereço aninhado |
| `PessoaJuridicaEnderecoListSerializer` | Listagem simplificada |
| `FilialEnderecoSerializer` | Vínculo Filial com endereço aninhado |
| `FilialEnderecoListSerializer` | Listagem simplificada |