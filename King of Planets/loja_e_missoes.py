import pygame
from utils import COLOR_CARD, COLOR_WHITE, COLOR_GREEN, COLOR_YELLOW, COLOR_BUTTON, COLOR_BUTTON_DISABLED

pygame.font.init()
font_ui = pygame.font.SysFont("Arial", 16, bold=True)
font_titulo_ui = pygame.font.SysFont("Arial", 22, bold=True)
font_pequena = pygame.font.SysFont("Arial", 12)

def desenhar_icone_missoes(screen, x, y):
    rect = pygame.Rect(x, y, 40, 40)
    pygame.draw.circle(screen, (0,0,0), (x+22, y+22), 20)
    pygame.draw.circle(screen, (255, 215, 0), (x+20, y+20), 20)
    txt = font_titulo_ui.render("★", True, (255, 255, 255))
    screen.blit(txt, (x + 10, y + 5))
    return rect

def desenhar_icone_loja(screen, x, y):
    rect = pygame.Rect(x, y, 50, 40)
    pygame.draw.polygon(screen, (200, 50, 50), [(x, y+20), (x+25, y), (x+50, y+20)])
    pygame.draw.rect(screen, (255, 255, 255), (x+5, y+20, 40, 20))
    txt = font_ui.render("$", True, (0, 100, 0))
    screen.blit(txt, (x + 20, y + 22))
    return rect

def desenhar_popup_missoes(screen, largura, altura, planeta):
    overlay = pygame.Surface((largura, altura)); overlay.set_alpha(180); overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))

    rect = pygame.Rect(50, 100, largura - 100, 300)
    pygame.draw.rect(screen, COLOR_CARD, rect, border_radius=15)
    pygame.draw.rect(screen, (255, 215, 0), rect, width=2, border_radius=15)

    txt_tit = font_titulo_ui.render(f"Missões: {planeta.nome}", True, COLOR_YELLOW)
    screen.blit(txt_tit, (rect.x + 20, rect.y + 20))

    cor1 = COLOR_GREEN if planeta.missao_nivel_feita else COLOR_WHITE
    st1 = "✓ Feita" if planeta.missao_nivel_feita else f"{planeta.nivel}/10"
    screen.blit(font_ui.render(f"1. Alcance Nível 10 ({st1})", True, cor1), (rect.x + 20, rect.y + 80))
    if not planeta.missao_nivel_feita:
        screen.blit(font_pequena.render("Prêmio: 5 Moedas", True, (150,150,150)), (rect.x + 20, rect.y + 100))

    cor2 = COLOR_GREEN if planeta.missao_meteoros_feita else COLOR_WHITE
    st2 = "✓ Feita" if planeta.missao_meteoros_feita else f"{planeta.missao_meteoros_progresso}/3"
    screen.blit(font_ui.render(f"2. Acerte 3 Meteoros ({st2})", True, cor2), (rect.x + 20, rect.y + 140))
    if not planeta.missao_meteoros_feita:
        screen.blit(font_pequena.render("Prêmio: 5 Moedas", True, (150,150,150)), (rect.x + 20, rect.y + 160))

    txt_f = font_pequena.render("Clique fora para fechar", True, (200,200,200))
    screen.blit(txt_f, (rect.centerx - txt_f.get_width()//2, rect.bottom - 30))

def desenhar_popup_loja(screen, largura, altura, imperio):
    overlay = pygame.Surface((largura, altura)); overlay.set_alpha(200); overlay.fill((0,0,0))
    screen.blit(overlay, (0,0))

    rect = pygame.Rect(40, 80, largura - 80, 400)
    pygame.draw.rect(screen, (50, 30, 30), rect, border_radius=15)
    pygame.draw.rect(screen, (200, 100, 100), rect, width=2, border_radius=15)

    txt_tit = font_titulo_ui.render("LOJA GALÁTICA", True, COLOR_WHITE)
    screen.blit(txt_tit, (rect.centerx - txt_tit.get_width()//2, rect.y + 20))
    
    txt_moedas = font_ui.render(f"Suas Moedas: {imperio.moedas_galaticas}", True, COLOR_YELLOW)
    screen.blit(txt_moedas, (rect.centerx - txt_moedas.get_width()//2, rect.y + 50))

    tem_auto = imperio.melhorias["auto_clicker"]
    cor1 = COLOR_GREEN if tem_auto else (COLOR_BUTTON if imperio.moedas_galaticas >= 25 else COLOR_BUTTON_DISABLED)
    rect1 = pygame.Rect(rect.x + 20, rect.y + 100, rect.width - 40, 60)
    pygame.draw.rect(screen, cor1, rect1, border_radius=10)
    nome1 = "auto_clicker (Comprado)" if tem_auto else "auto_clicker (25 Moedas)"
    screen.blit(font_ui.render(nome1, True, COLOR_WHITE), (rect1.x+10, rect1.y+10))
    screen.blit(font_pequena.render("Clica 20x por segundo.", True, (200,200,200)), (rect1.x+10, rect1.y+35))

    tem_chuva = imperio.melhorias["chuva_meteoros"]
    cor2 = COLOR_GREEN if tem_chuva else (COLOR_BUTTON if imperio.moedas_galaticas >= 30 else COLOR_BUTTON_DISABLED)
    rect2 = pygame.Rect(rect.x + 20, rect.y + 180, rect.width - 40, 60)
    pygame.draw.rect(screen, cor2, rect2, border_radius=10)
    nome2 = "Chuva Meteoros (Comprado)" if tem_chuva else "Chuva Meteoros (30 Moedas)"
    screen.blit(font_ui.render(nome2, True, COLOR_WHITE), (rect2.x+10, rect2.y+10))
    screen.blit(font_pequena.render("Meteoro traz +3 amigos.", True, (200,200,200)), (rect2.x+10, rect2.y+35))

    return rect1, rect2