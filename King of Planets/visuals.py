import pygame
import random

pygame.font.init()

# Cores
COLOR_PRODUCAO_EFEITO = (150, 255, 150)
COLOR_CLIQUE_EFEITO = (255, 255, 150)
COLOR_OUTLINE = (0, 0, 0)

font_efeito = pygame.font.SysFont("Comic Sans MS", 24, bold=True)

class Starfield:
    """Cria um fundo de estrelas animado."""
    def __init__(self, largura, altura, num_estrelas=100):
        self.largura = largura
        self.altura = altura
        self.estrelas = []
        for _ in range(num_estrelas):
            self.estrelas.append(self.criar_estrela())

    def criar_estrela(self):
        # [x, y, velocidade, tamanho]
        return [
            random.randint(0, self.largura),
            random.randint(0, self.altura),
            random.uniform(0.2, 1.5), # Velocidade
            random.randint(1, 2)      # Tamanho
        ]

    def update(self):
        for estrela in self.estrelas:
            estrela[1] += estrela[2] # Move para baixo (y)
            # Se sair da tela, volta pro topo em lugar aleatório
            if estrela[1] > self.altura:
                estrela[0] = random.randint(0, self.largura)
                estrela[1] = 0

    def draw(self, screen):
        for estrela in self.estrelas:
            pygame.draw.circle(screen, (200, 200, 255), (int(estrela[0]), int(estrela[1])), estrela[3])


class EfeitoFlutuante:
    """Controla um único texto flutuante."""
    def __init__(self, texto, x, y, cor, tempo_vida_ms=1000):
        self.x = x
        self.y = y
        self.cor = cor
        self.tempo_vida_total = tempo_vida_ms
        self.tempo_restante = tempo_vida_ms
        self.velocidade_y = -50 
        
        self.texto_surf = font_efeito.render(texto, True, self.cor)
        self.outline_surf = font_efeito.render(texto, True, COLOR_OUTLINE)

    def update(self, dt):
        self.tempo_restante -= dt * 1000
        self.y += self.velocidade_y * dt
        return self.tempo_restante > 0

    def draw(self, screen):
        alpha = 255
        if self.tempo_restante < 300:
            alpha = int((self.tempo_restante / 300) * 255)
            self.texto_surf.set_alpha(alpha)
            self.outline_surf.set_alpha(alpha)
        
        screen.blit(self.outline_surf, (self.x - 2, self.y))
        screen.blit(self.outline_surf, (self.x + 2, self.y))
        screen.blit(self.outline_surf, (self.x, self.y - 2))
        screen.blit(self.outline_surf, (self.x, self.y + 2))
        screen.blit(self.texto_surf, (self.x, self.y))


class GerenciadorDeEfeitos:
    def __init__(self):
        self.efeitos = []

    def spawn_production_effect(self, valor, x, y):
        if valor < 1: return 
        texto = f"+{int(valor)}"
        x_final = x + random.randint(-20, 20)
        y_final = y + random.randint(-10, 10)
        novo_efeito = EfeitoFlutuante(texto, x_final, y_final, COLOR_PRODUCAO_EFEITO)
        self.efeitos.append(novo_efeito)

    def spawn_click_effect(self, valor_ou_texto, x, y):
        if isinstance(valor_ou_texto, (int, float)):
            texto = f"+{int(valor_ou_texto)}"
        else:
            texto = str(valor_ou_texto)
        novo_efeito = EfeitoFlutuante(texto, x, y, COLOR_CLIQUE_EFEITO, tempo_vida_ms=800)
        self.efeitos.append(novo_efeito)

    def update_e_desenha(self, screen, dt):
        self.efeitos = [e for e in self.efeitos if e.update(dt)]
        for e in self.efeitos:
            e.draw(screen)