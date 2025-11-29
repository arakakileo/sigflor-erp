# Estrutura de Diretórios do Projeto

O projeto adota uma arquitetura modular e orientada a domínio, onde cada "App" Django representa um contexto de negócio bem definido e possui sua própria estrutura interna de camadas.

A estrutura principal de diretórios é a seguinte:

```text
sigflor_server/
├── src/
│   └── sigflor_server/
│       ├── manage.py
│       ├── core/               # Configurações centrais do Django (settings, urls)
│       └── apps/               # Contém todos os módulos de negócio
│           ├── comum/          # KERNEL: Dados mestres e entidades compartilhadas
│           │   ├── models/
│           │   │   ├── base.py
│           │   │   ├── anexos.py
│           │   │   ├── contatos.py
│           │   │   ├── ... (demais modelos)
│           │   ├── services/
│           │   ├── selectors/
│           │   ├── validators/
│           │   └── views/
│           │
│           └── rh/             # MÓDULO RH: Regras de negócio de pessoal
│               ├── models/
│               │   ├── cargos.py
│               │   ├── funcionarios.py
│               │   └── dependentes.py
│               ├── services/
│               ├── selectors/
│               └── views/
│
│           ├── sst/            # MÓDULO SST: Saúde e Segurança do Trabalho
│           │   ├── models/
│           │   ├── services/
│           │   └── views/
│           │
│           └── alojamento/     # MÓDULO ALOJAMENTO: Gestão de moradias
│               ├── models/
│               │   ├── alojamentos.py
│               │   └── ...
│               ├── services/
│               └── views/
│
└── docs/                     # Documentação do projeto (o que você está lendo)
```

## Detalhamento das Camadas (por App)

Dentro de cada `app` (como `comum` ou `rh`), a estrutura de camadas é padronizada:

-   `/models/`: Define a estrutura de dados do ORM, relacionamentos e constraints.
-   `/validators/`: Contém lógica pura e reutilizável de validação de dados (ex: validar CPF, CNPJ, telefone).
-   `/services/`: Implementa os casos de uso e as **regras de negócio**. É a camada mais importante, responsável pela orquestração das operações.
-   `/selectors/`: Otimiza e centraliza as consultas complexas ao banco de dados, retornando `QuerySets` performáticos.
-   `/views/`: Exclusivamente para a camada de API (DRF), responsável por lidar com `requests` e `responses`.
-   `/serializers/`: Converte os modelos em JSON e vice-versa, além de realizar validações de entrada da API.
