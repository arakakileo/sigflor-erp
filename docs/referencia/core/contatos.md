# Core — Contatos (Especificação Detalhada)

## 1. Visão Geral

A entidade **Contato** é um repositório centralizado para informações de contato como telefones e e-mails. Ela é uma entidade genérica, projetada para ser compartilhada e reutilizada por outros modelos (`PessoaFisica`, `PessoaJuridica`, `Filial`) através de tabelas de vínculo.

**Propósito Arquitetural:** Garantir a unicidade e a qualidade dos dados de contato. Um mesmo número de telefone ou e-mail é armazenado apenas uma vez, e os diferentes contextos de uso (principal, de emergência, etc.) são gerenciados nas tabelas de relacionamento.

**Status:** ✅ IMPLEMENTADO

---

## 2. Estrutura do Modelo (`comum.Contato`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **tipo** | `models.CharField` | `VARCHAR(20)` | `choices=Contato.Tipo.choices` (Enum: `CELULAR`, `FIXO`, `EMAIL`, `OUTRO`). |
| **valor** | `models.CharField` | `VARCHAR(150)` | **Regra:** Armazenado sem máscara. E-mails em minúsculas. |
| **tem_whatsapp**| `models.BooleanField`| `BOOLEAN` | `default=False`. **Regra:** Propriedade inerente ao contato. Aplicável apenas quando `tipo='CELULAR'`. |

### Campos Herdados (SoftDeleteModel)
- `created_at`, `updated_at`, `deleted_at`
- `created_by`, `updated_by`

**Constraint:** `UniqueConstraint` para a combinação `(tipo, valor)` onde `deleted_at IS NULL`, garantindo que cada contato ativo exista apenas uma vez na tabela.

### Propriedades Computadas
- **`valor_formatado`**: Retorna o telefone com máscara (ex: `(11) 99999-9999`).

### Enum `Tipo` para `Contato`
```python
class Tipo(models.TextChoices):
    CELULAR = 'CELULAR', 'Telefone Celular'
    FIXO = 'FIXO', 'Telefone Fixo'
    EMAIL = 'EMAIL', 'E-mail'
    OUTRO = 'OUTRO', 'Outro'
```

---

## 3. Relacionamentos (Modelo de Composição)

A associação é feita por tabelas de vínculo explícitas, que adicionam o contexto da relação.

### 3.1 Tabela de Vínculo: `PessoaFisicaContato`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`, `related_name='contatos_vinculados'`. |
| **contato** | `models.ForeignKey` para `Contato` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_fisica'`. |
| **principal** | `models.BooleanField` | `default=False`. |
| **contato_emergencia** | `models.BooleanField` | `default=False`. **Regra:** Indica se é contato de emergência. |

**Constraints:**
- `UniqueConstraint(fields=['pessoa_fisica', 'contato'])` - Impede duplicação de vínculo.
- `UniqueConstraint(fields=['pessoa_fisica'], condition=principal=True)` - Apenas um contato principal por pessoa.

**Tabela PostgreSQL:** `pessoas_fisicas_contatos`

### 3.2 Tabela de Vínculo: `PessoaJuridicaContato`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **pessoa_juridica** | `models.ForeignKey` para `PessoaJuridica` | `on_delete=models.CASCADE`, `related_name='contatos_vinculados'`. |
| **contato** | `models.ForeignKey` para `Contato` | `on_delete=models.CASCADE`, `related_name='vinculos_pessoa_juridica'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Constraints:**
- `UniqueConstraint(fields=['pessoa_juridica', 'contato'])` - Impede duplicação de vínculo.
- `UniqueConstraint(fields=['pessoa_juridica'], condition=principal=True)` - Apenas um contato principal por pessoa jurídica.

**Tabela PostgreSQL:** `pessoas_juridicas_contatos`

### 3.3 Tabela de Vínculo: `FilialContato`

| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **id** | `models.UUIDField` | PK padrão. |
| **filial** | `models.ForeignKey` para `Filial` | `on_delete=models.CASCADE`, `related_name='contatos_vinculados'`. |
| **contato** | `models.ForeignKey` para `Contato` | `on_delete=models.CASCADE`, `related_name='vinculos_filial'`. |
| **principal** | `models.BooleanField` | `default=False`. |

**Tabela PostgreSQL:** `filiais_contatos`

### Sobre o Campo `principal`

O campo `principal` nas tabelas de vínculo permite que uma entidade tenha múltiplos contatos, mas apenas um seja marcado como "principal". A constraint de unicidade garante isso ao nível do banco de dados.

---

## 4. Estratégia de Indexação

| Índice | Campos | Propósito |
| :--- | :--- | :--- |
| B-Tree | `tipo` | Filtros por tipo de contato |
| B-Tree | `valor` | Busca por valor específico |
| Único Composto | `(tipo, valor)` | Garantia de unicidade |

---

## 5. Camada de Serviço (`ContatoService`)

### Métodos de Criação

- **`create(*, tipo, valor, tem_whatsapp, created_by)`**:
  - Cria um contato sem vínculo com entidade.
  - Normaliza e valida o `valor` conforme o `tipo`.

- **`add_contato_to_pessoa_fisica(*, pessoa_fisica, tipo, valor, principal, contato_emergencia, tem_whatsapp, created_by)`**:
  - Executa um `get_or_create` na tabela `Contato` usando `tipo` e `valor`.
  - Cria a instância de `PessoaFisicaContato`.
  - Se `principal=True`, desmarca outros contatos como principal.
  - Retorna a instância de `PessoaFisicaContato`.

- **`add_contato_to_pessoa_juridica(*, pessoa_juridica, ...)`**: Análogo ao acima.
- **`add_contato_to_filial(*, filial, ...)`**: Análogo ao acima.

### Métodos de Atualização

- **`update(contato, updated_by, **kwargs)`**: Atualiza dados do contato.
- **`set_principal_pessoa_fisica(*, vinculo, updated_by)`**: Define como principal.
- **`set_principal_pessoa_juridica(*, vinculo, updated_by)`**: Análogo.
- **`set_principal_filial(*, vinculo, updated_by)`**: Análogo.

### Métodos de Exclusão

- **`delete(contato, user)`**: Soft delete do contato e todos os seus vínculos.
- **`remove_vinculo_pessoa_fisica(vinculo, user)`**: Remove apenas o vínculo.
- **`remove_vinculo_pessoa_juridica(vinculo, user)`**: Análogo.
- **`remove_vinculo_filial(vinculo, user)`**: Análogo.

### Métodos de Consulta

- **`get_contatos_pessoa_fisica(pessoa_fisica)`**: Retorna todos os contatos vinculados.
- **`get_contatos_pessoa_juridica(pessoa_juridica)`**: Análogo.
- **`get_contatos_filial(filial)`**: Análogo.
- **`get_contato_principal_pessoa_fisica(pessoa_fisica)`**: Retorna o contato principal.
- **`get_contato_principal_pessoa_juridica(pessoa_juridica)`**: Análogo.
- **`get_contato_principal_filial(filial)`**: Análogo.

---

## 6. Serializers

| Serializer | Propósito |
| :--- | :--- |
| `ContatoSerializer` | Leitura completa do contato |
| `ContatoCreateSerializer` | Criação com dados de vínculo |
| `PessoaFisicaContatoSerializer` | Vínculo PF com contato aninhado |
| `PessoaFisicaContatoListSerializer` | Listagem simplificada |
| `PessoaJuridicaContatoSerializer` | Vínculo PJ com contato aninhado |
| `PessoaJuridicaContatoListSerializer` | Listagem simplificada |
| `FilialContatoSerializer` | Vínculo Filial com contato aninhado |
| `FilialContatoListSerializer` | Listagem simplificada |
