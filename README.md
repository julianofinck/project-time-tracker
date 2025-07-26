# 📈⏰ Visualizador de Apontamentos 📊 - ([Deploy Interno](http://192.168.0.134:8050/))
[![Python 3.10.12](https://img.shields.io/badge/Python-3.10.12-yellow?style=flat&logo=python&logoColor=yellow&labelColor=&color=blue)](https://docs.python.org/3.9/)
[![Dash 2.17.1](https://img.shields.io/badge/Dash-2.17.1-black?style=flat&logo=plotly&logoColor=black&labelColor=white&color=black)](https://www.esri.com/pt-br/arcgis/products/arcgis-pro/overview)
[![Pandas 2.2.2](https://img.shields.io/badge/Pandas-2.2.2-red?style=flat&logo=pandas&logoColor=white&labelColor=%23130654&color=black)](https://pro.arcgis.com/en/pro-app/latest/arcpy/main/arcgis-pro-arcpy-reference.htm)



Esse projeto gera gráficos analíticos dinâmicos para gestão corporativa, utilizando sem seu core a biblioteca [Dash.plotly](https://dash.plotly.com/) do Python. Os dados da corporação são mantidos em arquivos Excel preenchidos diariamente pelos colaboradores, devendo ter as seguintes colunas:

| Colaborador | Data     | Projeto   | Produto   | Atividade                 | Horas totais |
|-------------|----------|-----------|-----------|---------------------------|--------------|
| João Maria  | 23/07/24 | Projeto 1 | Produto 3 | Documentação - Elaboração | 03:53        |


## ⬇️ Como instalar
```bash
# Caso não tenha, baixe uv (Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ative e sincronize o ambiente virtual
uv venv
uv sync

# Suba em produção
./run_server_prd.sh

# [DESENVOLVIMENTO]
# Instale os pre-commit hooks
uv run pre-commit install

# Rode em modo debug o 'run_server_dev.py"

```

## 🛠️ Como ele funciona?
Desde 02/02/2025 a dependência com a sincronização do OneDrive foi resolvida, acessando diratemente as planilhas pela API do Sharepoint

<div style="display: flex; justify-content: center; align-items: center; height: fit-content;">
    <img src="img/flowchart.svg" alt="Flowchart" style="background-color: white; height: 200px">
</div>

## 🌳 Estrutura do Projeto 🧬