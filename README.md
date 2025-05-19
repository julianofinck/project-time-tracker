# 📈⏰ Visualizador de Apontamentos 📊 - ([Deploy Interno](http://192.168.0.134:8050/))
[![Python 3.10.12](https://img.shields.io/badge/Python-3.10.12-yellow?style=flat&logo=python&logoColor=yellow&labelColor=&color=blue)](https://docs.python.org/3.9/)
[![Dash 2.17.1](https://img.shields.io/badge/Dash-2.17.1-black?style=flat&logo=plotly&logoColor=black&labelColor=white&color=black)](https://www.esri.com/pt-br/arcgis/products/arcgis-pro/overview)
[![Pandas 2.2.2](https://img.shields.io/badge/Pandas-2.2.2-red?style=flat&logo=pandas&logoColor=white&labelColor=%23130654&color=black)](https://pro.arcgis.com/en/pro-app/latest/arcpy/main/arcgis-pro-arcpy-reference.htm)



Esse projeto gera gráficos analíticos dinâmicos para gestão corporativa, utilizando sem seu core a biblioteca [Dash.plotly](https://dash.plotly.com/) do Python. Os dados da corporação são mantidos em arquivos Excel preenchidos diariamente pelos colaboradores, devendo ter as seguintes colunas:

| Colaborador | Data     | Projeto   | Produto   | Atividade                 | Horas totais |
|-------------|----------|-----------|-----------|---------------------------|--------------|
| João Maria  | 23/07/24 | Projeto 1 | Produto 3 | Documentação - Elaboração | 03:53        |


## ⬇️ Como instalar
Utilizando o [Poetry](https://python-poetry.org/docs/),
```shell
# Clone o repositório

# Entre no diretório raiz do projeto
cd <project-dir>

# Instale as dependencias
poetry install

# Ative o ambiente venv
poetry shell

# [SUBIR A APLICAÇÃO]
# Modo DEBUG
python run_server_debug.py

# Modo PRODUÇÃO
./run_server.sh
```

## 🛠️ Como ele funciona?
Desde 02/02/2025 a dependência com a sincronização do OneDrive foi resolvida, acessando diratemente as planilhas pela API do Sharepoint

<div style="display: flex; justify-content: center; align-items: center; height: fit-content;">
    <img src="img/flowchart.svg" alt="Flowchart" style="background-color: white; height: 200px">
</div>

## 🌳 Estrutura do Projeto 🧬
<pre>.
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/README.md">📄 README.md</a>
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app">📁 app</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/__init__.py">📄 __init__.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/alternative_to_onedrive.py">📄 alternative_to_onedrive.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/app_state.py">📄 app_state.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets">📁 assets</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css">📁 css</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/card.css">📄 card.css</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/header-selectors.css">📄 header-selectors.css</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/main.css">📄 main.css</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/root.css">📄 root.css</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/tab.css">📄 tab.css</a>
│   │   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/css/table.css">📄 table.css</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/favicon.ico">📄 favicon.ico</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/favicon_mock.ico">📄 favicon_mock.ico</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/assets/script.js">📄 script.js</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/cache">📁 cache</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/cache/state.pickle">📄 state.pickle</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/cache/valid_data.pickle">📄 valid_data.pickle</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks">📁 callbacks</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/__init__.py">📄 __init__.py</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/cards">📁 cards</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/cards/__init__.py">📄 __init__.py</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/cards/invalid_registers.py">📄 invalid_registers.py</a>
│   │   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/cards/team_commitment.py">📄 team_commitment.py</a>
│   │   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/cards/valid_registers.py">📄 valid_registers.py</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/headers.py">📄 headers.py</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/callbacks/read_excels_bar.py">📄 read_excels_bar.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/commitment_card_processor.py">📄 commitment_card_processor.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/languages">📁 languages</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/languages/__init__.py">📄 __init__.py</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/languages/translations.csv">📄 translations.csv</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/languages/translator.py">📄 translator.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/layout">📁 layout</a>
│   │   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/layout/__init__.py">📄 __init__.py</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/layout/layout.py">📄 layout.py</a>
│   ├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/mocks">📁 mocks</a>
│   │   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/mocks/mock.py">📄 mock.py</a>
│   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/utils">📁 utils</a>
│       └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/app/utils/logger.py">📄 logger.py</a>
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/img">📁 img</a>
│   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/img/flowchart.svg">📄 flowchart.svg</a>
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/logs">📁 logs</a>
│   └── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/logs/main.log">📄 main.log</a>
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/poetry.lock">📄 poetry.lock</a>
├── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/pyproject.toml">📄 pyproject.toml</a>
└── <a href="/home/julianofinck/codex/tabela-apontamentos/project-time-tracker/run.py">📄 run.py</a>

</pre>