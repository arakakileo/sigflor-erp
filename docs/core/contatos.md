# Core — Contatos (Especificação Detalhada)

## 1. Visão Geral

A entidade **Contato** é um repositório centralizado para informações de contato como telefones e e-mails. Ela é uma entidade genérica, projetada para ser compartilhada e reutilizada por outros modelos (`PessoaFisica`, `PessoaJuridica`) através de tabelas de vínculo.

**Propósito Arquitetural:** Garantir a unicidade e a qualidade dos dados de contato. Um mesmo número de telefone ou e-mail é armazenado apenas uma vez, e os diferentes contextos de uso (principal, de emergência, etc.) são gerenciados nas tabelas de relacionamento.

---

## 2. Estrutura do Modelo (`core.Contato`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **tipo** | `models.CharField` | `VARCHAR(20)` | `choices=Contato.Tipo.choices` (Enum: `CELULAR`, `FIXO`, `EMAIL`). |
| **valor** | `models.CharField` | `VARCHAR(150)` | **Regra:** Armazenado sem máscara. E-mails em minúsculas. |
| **tem_whatsapp**| `models.BooleanField`| `BOOLEAN` | `default=False`. **Regra:** Propriedade inerente ao contato. Aplicável apenas quando `tipo='CELULAR'`. |

**Constraint:** `UniqueConstraint` para a combinação `(tipo, valor)`, garantindo que cada contato exista apenas uma vez na tabela.

### Enum `Tipo` para `Contato`
```python
class Tipo(models.TextChoices):
    CELULAR = 'CELULAR', 'Telefone Celular'
    FIXO = 'FIXO', 'Telefone Fixo'
    EMAIL = 'EMAIL', 'E-mail'
```

---

## 3. Relacionamentos (Modelo de Composição)

A associação é feita por tabelas de vínculo explícitas, que adicionam o contexto da relação.

### Tabela de Vínculo Exemplo: `PessoaFisicaContato`
| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`. |
| **contato** | `models.ForeignKey` para `Contato` | `on_delete=models.CASCADE`. |
| **principal** | `models.BooleanField` | `default=False`. **Regra:** Contexto da relação. `UniqueConstraint` para `(pessoa_fisica, contato__tipo)` onde `principal=True`. |
| **contato_emergencia** | `models.BooleanField` | `default=False`. **Regra:** Contexto da relação. |

---

## 4. Estratégia de Indexação

-   **Índice Único Composto:** em `(tipo, valor)` (já garantido pelo `UniqueConstraint`).

---

## 5. Camada de Serviço (`ContatoService`)

A lógica de negócio é encapsulada no serviço.

-   **`add_contato_to_pessoa_fisica(*, pessoa_fisica: PessoaFisica, data: dict)`**:
    -   Recebe a instância da pessoa e um dicionário com os dados (`tipo`, `valor`, `principal`, `contato_emergencia`, `tem_whatsapp`).
    -   Normaliza e valida o `valor` conforme o `tipo`.
    -   **Lógica de Unicidade:** Executa um **`get_or_create`** na tabela `core.Contato` usando `tipo` e `valor`.
        -   Se o contato já existe, ele reutiliza a instância.
        -   Se não existe, ele cria a nova instância de `Contato`, definindo o `tem_whatsapp` se aplicável.
    -   Cria a instância de `PessoaFisicaContato`, estabelecendo o vínculo e definindo as flags contextuais `principal` e `contato_emergencia`.
    -   **Lógica de Negócio:** Se `principal=True`, o serviço garante (atomicamente) que qualquer outro contato do mesmo `tipo` para aquela `pessoa_fisica` seja desmarcado como principal.
