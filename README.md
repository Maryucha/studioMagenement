# studioMagenement

Aplicativo interativo construído com [Streamlit](https://streamlit.io/), [pandas](https://pandas.pydata.org/) e [SQLAlchemy](https://www.sqlalchemy.org/).  
Permite análise de dados e integração com banco PostgreSQL.

---

## 🚀 Como executar

### 🔹 Local (Linux/macOS)

1. Clone o repositório:

```bash
git clone https://github.com/SEU_USUARIO/studioMagenement.git
cd studioMagenement
```
2. Crie e ative o ambiente virtual:

```bash
    python3 -m venv .venv
    source .venv/bin/activate
```
ou 
```bash
 F1 -> Criar ambiente Python -> Seu Python Global -> requirements.txt
```

3. Executte o app:

```bash
    streamlit run Home.py
```

## ⚙️ Requisitos
- Python 3.11+

- PostgreSQL (local ou remoto)

- Variáveis de conexão definidas via .env ou .streamlit/secrets.toml