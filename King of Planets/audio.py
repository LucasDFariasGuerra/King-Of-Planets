import pygame
import os

class GerenciadorDeSom:
    def __init__(self):
        # Inicializa o mixer do Pygame se ainda não estiver
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"Erro ao iniciar audio: {e}")

        # Dicionário para guardar os sons carregados
        self.sons = {}
        
        # Tenta carregar os arquivos gerados
        # Certifique-se de ter rodado o gerar_sons.py antes!
        self.carregar_som("click", "sfx_click.wav", volume=0.4)
        self.carregar_som("upgrade", "sfx_upgrade.wav", volume=0.5)
        self.carregar_som("colonizar", "sfx_colonizar.wav", volume=0.6)

    def carregar_som(self, nome_chave, arquivo, volume=1.0):
        """Carrega um arquivo de som de forma segura."""
        if os.path.exists(arquivo):
            try:
                som = pygame.mixer.Sound(arquivo)
                som.set_volume(volume)
                self.sons[nome_chave] = som
            except Exception as e:
                print(f"Não foi possível carregar {arquivo}: {e}")
        else:
            print(f"Aviso: Arquivo de som '{arquivo}' não encontrado. Rode o script gerar_sons.py.")

    def play_click(self):
        """Toca o som de clique."""
        if "click" in self.sons:
            self.sons["click"].play()

    def play_upgrade(self):
        """Toca o som de upgrade."""
        if "upgrade" in self.sons:
            self.sons["upgrade"].play()

    def play_colonizar(self):
        """Toca o som de colonização."""
        if "colonizar" in self.sons:
            self.sons["colonizar"].play()