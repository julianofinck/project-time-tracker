# 📈⏰ Visualizador de Apontamentos 📊 - ([Deploy Interno](http://192.168.0.134:8050/))
[![Python 3.10.12](https://img.shields.io/badge/Python-3.10.12-yellow?style=flat&logo=python&logoColor=yellow&labelColor=&color=blue)](https://docs.python.org/3.9/)
[![Dash 2.17.1](https://img.shields.io/badge/Dash-2.17.1-black?style=flat&logo=plotly&logoColor=black&labelColor=white&color=black)](https://www.esri.com/pt-br/arcgis/products/arcgis-pro/overview)
[![Pandas 2.2.2](https://img.shields.io/badge/Pandas-2.2.2-red?style=flat&logo=pandas&logoColor=white&labelColor=%23130654&color=black)](https://pro.arcgis.com/en/pro-app/latest/arcpy/main/arcgis-pro-arcpy-reference.htm)



Esse projeto gera gráficos analíticos dinâmicos para gestão corporativa, utilizando sem seu core a biblioteca [Dash.plotly](https://dash.plotly.com/) do Python. Os dados da corporação são mantidos em arquivos Excel preenchidos diariamente pelos colaboradores, devendo ter as seguintes colunas:

| Colaborador | Data     | Projeto   | Produto   | Atividade                 | Horas totais |
|-------------|----------|-----------|-----------|---------------------------|--------------|
| João Maria  | 23/07/24 | Projeto 1 | Produto 3 | Documentação - Elaboração | 03:53        |


## ⬇️ Instalação
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

## Desenvolvimento
### Port-forwarding WSL-Windows
When running your application inside WSL, it may not be directly accessible from your Windows browser or external devices. To expose a WSL service (e.g., running on port 8050) to the host or network, set up port forwarding:

- Step 1 – Enable Port Forwarding (PowerShell as Administrator)

```powershell
# Forward traffic from Windows port 8050 to WSL port 8050
netsh interface portproxy add v4tov4 listenport=8050 listenaddress=0.0.0.0 connectport=8050 connectaddress=$($(wsl hostname -I).Trim())

# Confirm forwarding rule
netsh interface portproxy show v4tov4

# Remove rule if needed
netsh interface portproxy delete v4tov4 listenport=8050 listenaddress=0.0.0.0
```

- Step 2 – Allow Inbound Traffic in Windows Firewall
```powershell
New-NetFirewallRule -DisplayName "Allow Port 8050" `
    -Direction Inbound `
    -LocalPort 8050 `
    -Protocol TCP `
    -Action Allow `
    -Profile Any
# ⚠️ Note: This rule is permissive. For production environments, restrict by IP, profile, or scope as needed.
```

## 🛠️ Funcionamento
Desde 02/02/2025 a dependência com a sincronização do OneDrive foi resolvida, acessando diratemente as planilhas pela API do Sharepoint

<div style="display: flex; justify-content: center; align-items: center; height: fit-content;">
    <img src="img/flowchart.svg" alt="Flowchart" style="background-color: white; height: 200px">
</div>


---

## 🌳 Estrutura do Projeto 