import pygame
import random

# Inicializa as fontes aqui, pois este módulo cuida do visual
pygame.font.init()

# --- Cores dos Efeitos ---
COLOR_PRODUCAO_EFEITO = (150, 255, 150) # Verde para produção
COLOR_CLIQUE_EFEITO = (255, 255, 150)   # Amarelo para cliques
COLOR_OUTLINE = (0, 0, 0)         # Contorno preto

# --- Fontes dos Efeitos ---
font_efeito = pygame.font.SysFont("Comic Sans MS", 24, bold=True)


class EfeitoFlutuante:
    """
    Controla um único texto flutuante (ex: '+10')
    """
    def __init__(self, texto, x, y, cor, tempo_vida_ms=1000):
        self.x = x
        self.y = y
        self.cor = cor
        self.tempo_vida_total = tempo_vida_ms
        self.tempo_restante = tempo_vida_ms
        self.velocidade_y = -50 # Pixels por segundo (para cima)
        
        # Pré-renderiza o texto para performance
        self.texto_surf = font_efeito.render(texto, True, self.cor)
        self.outline_surf = font_efeito.render(texto, True, COLOR_OUTLINE)

    def update(self, delta_time_segundos):
        """Atualiza a posição e o tempo de vida."""
        self.y += self.velocidade_y * delta_time_segundos
        self.tempo_restante -= delta_time_segundos * 1000 # delta_time está em segundos
        
        # Retorna True se ainda estiver vivo, False se deve ser removido
        return self.tempo_restante > 0

    def draw(self, screen):
        """Desenha o efeito na tela com contorno e transparência."""
        
        # Calcula a opacidade (alpha) baseada no tempo restante
        alpha = int(255 * (self.tempo_restante / self.tempo_vida_total))
        alpha = max(0, min(255, alpha)) # Garante que alpha esteja entre 0-255

        # Cria cópias para aplicar o alpha
        texto_surf_alpha = self.texto_surf.copy()
        outline_surf_alpha = self.outline_surf.copy()
        
        texto_surf_alpha.set_alpha(alpha)
        outline_surf_alpha.set_alpha(alpha)
        
        # Desenha o contorno
        outline_offset = 2
        for dx in range(-outline_offset, outline_offset + 1):
            for dy in range(-outline_offset, outline_offset + 1):
                if dx != 0 or dy != 0:
                    screen.blit(outline_surf_alpha, (self.x + dx, self.y + dy))
        
        # Desenha o texto principal
        screen.blit(texto_surf_alpha, (self.x, self.y))


class GerenciadorDeEfeitos:
    """
    Controla todos os efeitos flutuantes na tela.
    """
    def __init__(self):
        self.efeitos = []

    def spawn_production_effect(self, valor, x, y):
        """Cria um novo efeito de produção (verde)."""
        if valor < 1:
            return # Não mostra efeitos para valores menores que 1
        
        texto = f"+{int(valor)}"
        # Adiciona variação aleatória na posição inicial
        x_final = x + random.randint(-20, 20)
        y_final = y + random.randint(-10, 10)
        
        novo_efeito = EfeitoFlutuante(texto, x_final, y_final, COLOR_PRODUCAO_EFEITO)
        self.efeitos.append(novo_efeito)

    def spawn_click_effect(self, valor, x, y):
        """Cria um novo efeito de clique (amarelo) no local do mouse."""
        texto = f"+{int(valor)}"
        novo_efeito = EfeitoFlutuante(texto, x, y, COLOR_CLIQUE_EFEITO, tempo_vida_ms=700)
        self.efeitos.append(novo_efeito)

    def update_e_desenha(self, screen, delta_time_segundos):
        """Chama update e draw para todos os efeitos."""
        
        # Itera sobre uma cópia da lista para poder remover itens
        for efeito in self.efeitos[:]:
            esta_vivo = efeito.update(delta_time_segundos)
            if esta_vivo:
                efeito.draw(screen)
            else:
                self.efeitos.remove(efeito) # Remove efeitos mortos