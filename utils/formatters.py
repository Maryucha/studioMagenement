"""
utils.py
Funções utilitárias para o sistema
"""
from datetime import datetime
import locale
import urllib.parse
from decimal import Decimal
TAXA_CAMBIO_FIXA = Decimal("6.42")

# Tentativa de configurar o locale para português brasileiro
# Se não funcionar, usa configurações padrão
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR')
    except:
        pass  # Se falhar, mantém o locale padrão

def formatar_data_pt(data):
    """Formata uma data no padrão brasileiro (dia/mês/ano)"""
    if not data:
        return ""
    if isinstance(data, str):
        try:
            data = datetime.fromisoformat(data)
        except ValueError:
            return data
    return data.strftime("%d/%m/%Y")

def formatar_data_hora_pt(data_hora):
    """Formata uma data e hora no padrão brasileiro (dia/mês/ano hora:minuto)"""
    if not data_hora:
        return ""
    if isinstance(data_hora, str):
        try:
            data_hora = datetime.fromisoformat(data_hora)
        except ValueError:
            return data_hora
    return data_hora.strftime("%d/%m/%Y %H:%M")

def converter_para_euro(valor):
    """
    Converte um valor para euro usando uma taxa de câmbio fixa.
    
    Args:
        valor (float or Decimal): Valor original em outra moeda (ex: BRL).
    
    Returns:
        Decimal: Valor convertido para euro.
    """
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    return valor / TAXA_CAMBIO_FIXA

def formatar_moeda_euro(valor):
    """
    Formata um número como moeda no padrão euro (ex: 1.234,56 €).
    
    Args:
        valor (float or int): Valor numérico a ser formatado.

    Returns:
        str: Valor formatado como moeda em euro.
    """
    return f"{valor:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def categorias_servicos():
    """Lista de categorias de serviços padrão"""
    return [
        "Unhas",
        "Massagem",
        "Sobrancelhas",
        "Depilação",
        "Pestanas",
        "Outro"
    ]

def categorias_custos():
    """Lista de categorias de custos padrão"""
    return [
        "Aluguel",
        "Água",
        "Energia",
        "Internet",
        "Telefone",
        "Materiais",
        "Salários",
        "Comissões",
        "Marketing",
        "Manutenção",
        "Impostos",
        "Seguros",
        "Outros"
    ]

def status_agendamento():
    """Lista de status de agendamento válidos"""
    return [
        "pendente",
        "realizado",
        "cancelado"
    ]

def tipos_custos():
    """Lista de tipos de custos válidos"""
    return [
        "fixo",
        "variavel"
    ]

def uf_brasil():
    """Lista de UFs brasileiras"""
    return [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", 
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]

def gerar_link_whatsapp(telefone, mensagem=""):
    """
    Gera um link para o WhatsApp com número de telefone e mensagem predefinida
    
    Args:
        telefone (str): Número de telefone no formato brasileiro (pode incluir formatação)
        mensagem (str): Mensagem a ser enviada (opcional)
        
    Returns:
        str: Link para iniciar conversa no WhatsApp
    """
    # Garantir que o telefone tenha o formato correto para o WhatsApp
    telefone_limpo = limpar_telefone(telefone)
    
    # Se não tiver código do país, adiciona o Brasil (+55)
    if len(telefone_limpo) <= 11:  # DDD + número
        telefone_whatsapp = f"55{telefone_limpo}"
    else:
        telefone_whatsapp = telefone_limpo
    
    # Codificar a mensagem para URL
    mensagem_url = urllib.parse.quote(mensagem)
    
    # Gerar o link do WhatsApp
    return f"https://wa.me/{telefone_whatsapp}?text={mensagem_url}"

def limpar_telefone(telefone):
    """Remove caracteres não numéricos do telefone"""
    if not telefone:
        return ""
    return ''.join(filter(str.isdigit, str(telefone)))
