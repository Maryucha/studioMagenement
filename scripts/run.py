import os
import subprocess
from infra.database import mostrar_conexao_atual

def set_env_and_run(env_type):
    """Define o ambiente e roda o Streamlit"""
    os.environ["APP_ENV"] = env_type
    print("\n=== Configuração de Conexão ===")
    mostrar_conexao_atual()
    print("\n=== Iniciando Streamlit ===")
    subprocess.run(["streamlit", "run", "Home.py"])

def dev():
    """Roda o app conectando ao Docker local"""
    print("🐳 Iniciando em modo desenvolvimento (Docker local)...")
    set_env_and_run("local_docker")

def neon():
    """Roda o app conectando ao Neon"""
    print("🚀 Iniciando em modo Neon...")
    set_env_and_run("local_neon")

def init():
    """Inicializa o banco de dados"""
    print("🔧 Inicializando banco de dados...")
    from infra.database import inicializar_banco
    mostrar_conexao_atual()
    inicializar_banco()
    print("✅ Banco inicializado com sucesso!") 