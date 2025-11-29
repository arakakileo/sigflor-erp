# Core — Documentos (Especificação Detalhada)

## 1. Visão Geral

O submódulo de **Documentos** fornece uma estrutura centralizada para o upload e armazenamento de arquivos formais e categorizados. Diferente de `Anexos` (informais), `Documentos` possuem metadados estruturados como tipo, data de emissão e validade.

**Propósito Arquitetural:** Centralizar a gestão de arquivos formais, permitindo o reaproveitamento da lógica de armazenamento, validação e controle de acesso, e associando-os a diferentes entidades através de tabelas de vínculo.

---

## 2. Estrutura do Modelo (`core.Documento`)

| Atributo | Tipo Django | Tipo PostgreSQL | Constraints e Regras |
| :--- | :--- | :--- | :--- |
| **id** | `models.UUIDField` | `UUID` | `primary_key=True`, `default=uuid.uuid4`, `editable=False` |
| **tipo** | `models.CharField` | `VARCHAR(50)` | `choices=Documento.Tipo.choices` (Enum). `null=False`, `blank=False`. |
| **descricao** | `models.TextField` | `TEXT` | `null=True`, `blank=True`. |
| **arquivo** | `models.FileField` | `VARCHAR(255)` | `upload_to='documentos/%Y/%m/'`. O arquivo físico. |
| **nome_original**| `models.CharField` | `VARCHAR(255)` | Nome do arquivo no momento do upload. |
| **mimetype** | `models.CharField` | `VARCHAR(100)` | Tipo MIME do arquivo (ex: `application/pdf`). |
| **tamanho** | `models.PositiveIntegerField` | `INTEGER` | Tamanho do arquivo em bytes. |
| **data_emissao** | `models.DateField` | `DATE` | `null=True`, `blank=True`. |
| **data_validade** | `models.DateField` | `DATE` | `null=True`, `blank=True`. **Regra:** Importante para CNH, ASO, etc. |

### Enum `Tipo` para `Documento`
```python
class Tipo(models.TextChoices):
    RG = 'RG', 'RG'
    CNH = 'CNH', 'Carteira Nacional de Habilitação'
    CPF = 'CPF', 'Cadastro de Pessoas Físicas'
    TITULO_ELEITOR = 'TITULO_ELEITOR', 'Título de Eleitor'
    CERTIDAO_NASCIMENTO_CASAMENTO = 'CERTIDAO_NASCIMENTO_CASAMENTO', 'Certidão de Nascimento/Casamento'
    COMPROVANTE_ENDERECO = 'COMPROVANTE_ENDERECO', 'Comprovante de Endereço'
    CARTAO_SUS = 'CARTAO_SUS', 'Cartão do SUS'
    CARTEIRA_VACINA = 'CARTEIRA_VACINA', 'Carteira de Vacinação (Geral)'
    COMPROVANTE_PIS_NIS = 'COMPROVANTE_PIS_NIS', 'Comprovante PIS/NIS'
    CTPS = 'CTPS', 'Carteira de Trabalho Digital'
    CERTIDAO_NASCIMENTO_DEPENDENTE = 'CERTIDAO_NASCIMENTO_DEPENDENTE', 'Certidão de Nascimento de Dependente'
    CARTEIRA_VACINA_DEPENDENTE = 'CARTEIRA_VACINA_DEPENDENTE', 'Carteira de Vacinação de Dependente'
    DECLARACAO_ESCOLAR_DEPENDENTE = 'DECLARACAO_ESCOLAR_DEPENDENTE', 'Declaração de Matrícula Escolar de Dependente'
    CARTAO_CONTA_BANCO = 'CARTAO_CONTA_BANCO', 'Cartão/Comprovante de Conta Bancária'
    FOTO_3X4 = 'FOTO_3X4', 'Foto 3x4'
    NADA_CONSTA_DETRAN = 'NADA_CONSTA_DETRAN', 'Nada Consta DETRAN'
    CURSO_MOOP = 'CURSO_MOOP', 'Certificado Curso MOOP'
    CURSO_PASSAGEIROS = 'CURSO_PASSAGEIROS', 'Certificado Curso Transporte de Passageiros'
    CURSO_MAQUINAS_AGRICOLAS = 'CURSO_MAQUINAS_AGRICOLAS', 'Certificado Curso Operação de Máquinas Agrícolas'
    ASO = 'ASO', 'Atestado de Saúde Ocupacional (Documento PDF)'
    OUTROS = 'OUTROS', 'Outros Documentos'
```
**Nota:** Esta lista deve ser configurável, idealmente via `Parâmetros Globais`.

---

## 3. Relacionamentos (Modelo de Composição)

### Tabela de Vínculo Exemplo: `PessoaFisicaDocumento`
| Atributo | Tipo Django | Constraints e Regras |
| :--- | :--- | :--- |
| **pessoa_fisica** | `models.ForeignKey` para `PessoaFisica` | `on_delete=models.CASCADE`. |
| **documento** | `models.ForeignKey` para `Documento` | `on_delete=models.CASCADE`. |
| **principal** | `models.BooleanField` | `default=False`. **Regra:** `UniqueConstraint` para `(pessoa_fisica, documento__tipo)` onde `principal=True`. |

**Nota:** O campo `principal` na tabela de vínculo permite, por exemplo, que uma pessoa tenha múltiplas CNHs (uma vencida e uma atual), mas apenas uma seja marcada como a "principal" ou "vigente" para aquele tipo.

---

## 4. Estratégia de Indexação

-   **Índice Padrão (B-Tree):** no campo `data_validade` para otimizar a busca por documentos vencidos ou a vencer.
-   **Índice Composto:** em `(tipo, data_emissao)`.

---

## 5. Camada de Serviço (`DocumentoService`)

-   **`add_documento_to_pessoa_fisica(*, pessoa_fisica: PessoaFisica, data: dict, file)`**:
    -   Recebe a instância da pessoa, os metadados do documento (`tipo`, `data_emissao`, etc.) e o arquivo enviado.
    -   **Lógica de Upload:** Interage com o storage backend do Django para salvar o arquivo.
    -   Extrai metadados do arquivo (`nome_original`, `mimetype`, `tamanho`) e os salva.
    -   Cria a instância de `Documento`.
    -   Cria a instância de `PessoaFisicaDocumento` para estabelecer o vínculo.
    -   **Lógica de Negócio:** Se `principal=True`, garante que o `UniqueConstraint` seja respeitado, desmarcando outros documentos do mesmo tipo para aquela pessoa.
-   **`get_documentos_a_vencer(dias: int)`**: Um seletor/serviço que retorna documentos cuja `data_validade` está dentro do prazo especificado.