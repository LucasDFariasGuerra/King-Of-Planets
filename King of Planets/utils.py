import os
from colorama import init, Fore, Style

init(autoreset=True)

COR_PONTOS = Fore.BLUE + Style.BRIGHT  
COR_TITULO = Fore.CYAN + Style.BRIGHT
COR_PLANETA = Fore.WHITE + Style.BRIGHT
COR_SUCESSO = Fore.GREEN
COR_AVISO = Fore.YELLOW + Style.BRIGHT 
COR_ERRO = Fore.RED
COR_EVENTO = Fore.MAGENTA 

COLOR_BG = (10, 10, 30)           
COLOR_CARD = (30, 30, 50)         
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

COLOR_BUTTON = (50, 50, 80)
COLOR_BUTTON_DISABLED = (30, 30, 30)
COLOR_BARRA_FUNDO = (0, 0, 0)
COLOR_BARRA_PREENCHIMENTO = (255, 255, 100)
COLOR_PRESTIGIO = (100, 255, 100)

COLOR_GREEN = (100, 255, 100)
COLOR_BLUE = (100, 150, 255)
COLOR_YELLOW = (255, 255, 100)
COLOR_RED = (255, 100, 100)
COLOR_PONTOS_RGB = (100, 200, 255) 

COLOR_INPUT_ACTIVE = (100, 100, 150)
COLOR_INPUT_INACTIVE = (50, 50, 70)


def limpar_tela():
    """Limpa o console para uma UI mais limpa."""
    os.system('cls' if os.name == 'nt' else 'clear')

def formatar_numero_jogo(valor):
    """
    Formata números grandes para 1K, 1M, 1B, etc.
    Usa vírgula como separador decimal (PT-BR).
    """
    valor = float(valor)
    
    if valor >= 1_000_000_000_000_000:
        texto = f"{valor/1_000_000_000_000_000:.2f}Q"
    elif valor >= 1_000_000_000_000:
        texto = f"{valor/1_000_000_000_000:.2f}T"
    elif valor >= 1_000_000_000:
        texto = f"{valor/1_000_000_000:.2f}B"
    elif valor >= 1_000_000:
        texto = f"{valor/1_000_000:.2f}M"
    elif valor >= 1_000:
        texto = f"{valor/1_000:.2f}K"
    else:
        return str(int(valor))

    return texto.replace(".", ",")