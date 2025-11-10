import os
from colorama import init, Fore, Style

# Inicializa o Colorama. 
# A partir de agora, qualquer print colorido funcionará.
# autoreset=True faz com que cada print volte à cor padrão.
init(autoreset=True)

# --- Constantes de Cores ---
# Desta forma, podemos mudar todas as cores do jogo em um só lugar.

# Pedido especial: Pontos em Azul
COR_PONTOS = Fore.BLUE + Style.BRIGHT  

COR_TITULO = Fore.CYAN + Style.BRIGHT
COR_PLANETA = Fore.WHITE + Style.BRIGHT
COR_SUCESSO = Fore.GREEN
COR_AVISO = Fore.YELLOW + Style.BRIGHT # Para custos e alertas
COR_ERRO = Fore.RED
COR_EVENTO = Fore.MAGENTA # Para colonização de novos planetas


# --- Funções Utilitárias ---

def limpar_tela():
    """Limpa o console para uma UI mais limpa."""
    # 'nt' é windows, 'posix' é Mac/Linux
    os.system('cls' if os.name == 'nt' else 'clear')