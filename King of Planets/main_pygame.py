import pygame
import sys
import time

# Módulos do Jogo
from modelos import Imperio
from visuals import GerenciadorDeEfeitos
# NOVOS MÓDULOS DE AUTENTICAÇÃO
from usuarios import registrar_usuario, login_usuario
from database import carregar_json, salvar_json # Usaremos no futuro para salvar o jogo

# --- Configurações Iniciais ---
pygame.init()
pygame.font.init()

# --- Constantes da Janela ---
LARGURA_TELA = 400
ALTURA_TELA = 600
screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
clock = pygame.time.Clock()

# --- Cores ---
COLOR_BG = (10, 10, 30)
COLOR_CARD = (30, 30, 50)
COLOR_BUTTON = (50, 50, 80)
COLOR_BUTTON_DISABLED = (30, 30, 30)
COLOR_WHITE = (255, 255, 255)
COLOR_GREEN = (100, 255, 100)
COLOR_BLUE = (100, 150, 255)
COLOR_YELLOW = (255, 255, 100)
COLOR_RED = (255, 100, 100)
COLOR_INPUT_ACTIVE = (150, 150, 200)
COLOR_INPUT_INACTIVE = (80, 80, 110)

# --- Fontes ---
font_titulo = pygame.font.SysFont("Segoe UI", 30, bold=True)
font_pontos = pygame.font.SysFont("Segoe UI", 22, bold=True)
font_corpo = pygame.font.SysFont("Segoe UI", 16)
font_botao = pygame.font.SysFont("Segoe UI", 16, bold=True)
font_botao_pequeno = pygame.font.SysFont("Segoe UI", 12)
font_input = pygame.font.SysFont("Segoe UI", 20)
font_feedback = pygame.font.SysFont("Segoe UI", 14, bold=True)

# --- Variáveis de Imagem (Carregar uma vez) ---
try:
    planeta_clicker_img = pygame.transform.scale(pygame.image.load("planeta_base.png").convert_alpha(), (150, 150))
    planeta_clicker_rect = planeta_clicker_img.get_rect(center=(LARGURA_TELA // 2, 180))
except pygame.error:
    planeta_clicker_img = None
    planeta_clicker_rect = pygame.Rect(LARGURA_TELA // 2 - 75, 180 - 75, 150, 150)


# --- Classe Auxiliar para Input de Texto ---
class InputBox:
    def __init__(self, x, y, w, h, is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INPUT_INACTIVE
        self.text = ''
        self.text_surface = font_input.render(self.text, True, COLOR_WHITE)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = COLOR_INPUT_ACTIVE if self.active else COLOR_INPUT_INACTIVE
        
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return "enter" # Sinaliza que Enter foi pressionado
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=5)
        
        # Desenha texto com '*' se for senha
        display_text = self.text
        if self.is_password:
            display_text = '*' * len(self.text)
            
        self.text_surface = font_input.render(display_text, True, COLOR_WHITE)
        screen.blit(self.text_surface, (self.rect.x + 10, self.rect.y + (self.rect.h - self.text_surface.get_height()) // 2))


def draw_text(text, font, color, x, y, anchor="topleft"):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if anchor == "topleft":
        text_rect.topleft = (x, y)
    elif anchor == "center":
        text_rect.center = (x, y)
    elif anchor == "midtop":
        text_rect.midtop = (x, y)
    screen.blit(text_surf, text_rect)

# --- Funções de Tela (Estados) ---

def run_auth_screen(estado_inicial="LOGIN"):
    """
    Controla as telas de Login e Registro.
    Retorna o nome do usuário logado quando o login é bem-sucedido.
    """
    estado_auth = estado_inicial
    
    # Inputs
    input_user = InputBox(LARGURA_TELA // 2 - 150, 200, 300, 40)
    input_pass = InputBox(LARGURA_TELA // 2 - 150, 260, 300, 40, is_password=True)
    inputs = [input_user, input_pass]
    
    # Botões (Rects para checar clique)
    btn_login_rect = pygame.Rect(LARGURA_TELA // 2 - 150, 330, 300, 40)
    btn_goto_reg_rect = pygame.Rect(LARGURA_TELA // 2 - 150, 380, 300, 40)
    btn_register_rect = pygame.Rect(LARGURA_TELA // 2 - 150, 330, 300, 40) # Mesmo lugar do login
    btn_goto_login_rect = pygame.Rect(LARGURA_TELA // 2 - 150, 380, 300, 40)
    
    feedback_msg = ""
    feedback_color = COLOR_RED
    
    while True:
        click_pos = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_pos = event.pos
            
            # Passa eventos para os inputs
            enter_pressed = False
            for box in inputs:
                if box.handle_event(event) == "enter":
                    enter_pressed = True

            if enter_pressed:
                 # Simula clique no botão principal
                 if estado_auth == "LOGIN":
                     click_pos = btn_login_rect.center
                 else:
                     click_pos = btn_register_rect.center

        # --- Lógica de Clique ---
        if click_pos:
            if estado_auth == "LOGIN":
                if btn_login_rect.collidepoint(click_pos):
                    # Tenta logar
                    user = input_user.text
                    pwd = input_pass.text
                    sucesso, msg = login_usuario(user, pwd)
                    if sucesso:
                        return user # << SUCESSO! Retorna o nome do usuário
                    else:
                        feedback_msg = msg
                        feedback_color = COLOR_RED
                        
                elif btn_goto_reg_rect.collidepoint(click_pos):
                    estado_auth = "REGISTRO"
                    feedback_msg = ""
                    input_user.text = ""
                    input_pass.text = ""
                    
            elif estado_auth == "REGISTRO":
                if btn_register_rect.collidepoint(click_pos):
                    # Tenta registrar
                    user = input_user.text
                    pwd = input_pass.text
                    sucesso, msg = registrar_usuario(user, pwd)
                    if sucesso:
                        feedback_msg = msg
                        feedback_color = COLOR_GREEN
                        estado_auth = "LOGIN" # Volta pro login
                    else:
                        feedback_msg = msg
                        feedback_color = COLOR_RED
                        
                elif btn_goto_login_rect.collidepoint(click_pos):
                    estado_auth = "LOGIN"
                    feedback_msg = ""
                    input_user.text = ""
                    input_pass.text = ""

        # --- Desenho ---
        screen.fill(COLOR_BG)
        
        # Título
        draw_text("King of Planets", font_titulo, COLOR_WHITE, LARGURA_TELA // 2, 100, anchor="center")
        
        if estado_auth == "LOGIN":
            draw_text("Login", font_pontos, COLOR_WHITE, LARGURA_TELA // 2, 150, anchor="center")
            # Botões
            pygame.draw.rect(screen, COLOR_BUTTON, btn_login_rect, border_radius=5)
            draw_text("Entrar", font_botao, COLOR_WHITE, btn_login_rect.centerx, btn_login_rect.centery, anchor="center")
            pygame.draw.rect(screen, COLOR_CARD, btn_goto_reg_rect, border_radius=5)
            draw_text("Não tem conta? Registre-se", font_botao, COLOR_WHITE, btn_goto_reg_rect.centerx, btn_goto_reg_rect.centery, anchor="center")
            
        elif estado_auth == "REGISTRO":
            draw_text("Registro", font_pontos, COLOR_WHITE, LARGURA_TELA // 2, 150, anchor="center")
            # Botões
            pygame.draw.rect(screen, COLOR_BUTTON, btn_register_rect, border_radius=5)
            draw_text("Registrar", font_botao, COLOR_WHITE, btn_register_rect.centerx, btn_register_rect.centery, anchor="center")
            pygame.draw.rect(screen, COLOR_CARD, btn_goto_login_rect, border_radius=5)
            draw_text("Já tem conta? Faça Login", font_botao, COLOR_WHITE, btn_goto_login_rect.centerx, btn_goto_login_rect.centery, anchor="center")

        # Inputs
        draw_text("Usuário:", font_corpo, COLOR_WHITE, input_user.rect.x, input_user.rect.y - 20)
        draw_text("Senha:", font_corpo, COLOR_WHITE, input_pass.rect.x, input_pass.rect.y - 20)
        for box in inputs:
            box.draw(screen)
            
        # Feedback
        if feedback_msg:
            draw_text(feedback_msg, font_feedback, feedback_color, LARGURA_TELA // 2, 440, anchor="center")

        pygame.display.flip()
        clock.tick(60)

def run_game_loop(usuario_logado):
    """
    O loop principal do jogo que já tínhamos.
    Agora ele CARREGA e SALVA o progresso do usuário.
    """
    
    # --- Configurações do Jogo ---
    
    # --- LÓGICA DE CARREGAMENTO ---
    save_filename = f"{usuario_logado}_save.json"
    dados_salvos = carregar_json(save_filename)
    
    if dados_salvos:
        print(f"Carregando progresso de {usuario_logado}...")
        imperio = Imperio.from_dict(dados_salvos)
    else:
        print(f"Nenhum progresso encontrado. Criando novo jogo para {usuario_logado}...")
        imperio = Imperio()
    
    gerenciador_de_efeitos = GerenciadorDeEfeitos()
    # ... (resto das variáveis) ...
    production_timer = 0.0
    INTERVALO_PRODUCAO_SEG = 0.5
    scroll_y = 0
    ALTURA_CARTAO_PLANETA = 100
    PADDING_CARTAO = 10
    scroll_area_rect = pygame.Rect(0, 270, LARGURA_TELA, ALTURA_TELA - 270 - 70)
    
    ultimo_update_time = time.time()
    
    # O loop principal do JOGO
    running = True
    while running:
        # --- 1. Cálculo do Delta Time ---
        agora = time.time()
        delta_time_segundos = agora - ultimo_update_time 
        ultimo_update_time = agora
        
        click_pos = None # Reseta o clique
        mouse_pos = pygame.mouse.get_pos()
        
        # --- 2. Lógica do Jogo (Sincronizada) ---
        production_timer += delta_time_segundos
        while production_timer >= INTERVALO_PRODUCAO_SEG:
            pontos_ganhos = imperio.produzir_recursos_intervalo(INTERVALO_PRODUCAO_SEG)
            if pontos_ganhos >= 1:
                gerenciador_de_efeitos.spawn_production_effect(pontos_ganhos, planeta_clicker_rect.centerx, planeta_clicker_rect.top)
            production_timer -= INTERVALO_PRODUCAO_SEG

        # --- 3. Manipulação de Eventos (Input) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                
                # --- LÓGICA DE SALVAMENTO ---
                print(f"Salvando progresso de {usuario_logado}...")
                dados_para_salvar = imperio.to_dict()
                salvar_json(f"{usuario_logado}_save.json", dados_para_salvar)
                print("Progresso salvo. Saindo...")
                
                running = False # Encerra o loop do JOGO, voltando para main()
            
            if event.type == pygame.MOUSEWHEEL:
                if scroll_area_rect.collidepoint(mouse_pos):
                    scroll_y -= event.y * 30
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click_pos = event.pos 
                    
        # --- 4. Lógica de Scroll (Clamp) ---
        total_content_height = len(imperio.planetas) * (ALTURA_CARTAO_PLANETA + PADDING_CARTAO)
        max_scroll_y = max(0, total_content_height - scroll_area_rect.height)
        scroll_y = max(0, min(scroll_y, max_scroll_y))

        # --- 5. Desenho (Renderização) ---
        screen.fill(COLOR_BG)

        # --- A. UI Fixa Superior (Pontos e Planeta Clicker) ---
        draw_text("Pontos Galáticos:", font_titulo, COLOR_WHITE, LARGURA_TELA // 2, 20, anchor="midtop")
        draw_text(f"{int(imperio.pontos_galaticos)}", font_pontos, COLOR_BLUE, LARGURA_TELA // 2, 50, anchor="midtop")
        draw_text(f"(+ {imperio.get_producao_total_ps():.2f} /s)", font_corpo, COLOR_GREEN, LARGURA_TELA // 2, 80, anchor="midtop")
        
        if planeta_clicker_img:
            screen.blit(planeta_clicker_img, planeta_clicker_rect)
        
        if click_pos and planeta_clicker_rect.collidepoint(click_pos):
            pontos_ganhos = imperio.clicar_planeta()
            gerenciador_de_efeitos.spawn_click_effect(pontos_ganhos, click_pos[0], click_pos[1])
            click_pos = None

        # --- B. Efeitos Flutuantes ---
        gerenciador_de_efeitos.update_e_desenha(screen, delta_time_segundos)

        # --- C. Área Rolável (Cartões de Planetas) ---
        screen.set_clip(scroll_area_rect)
        y_offset_cartoes = scroll_area_rect.top - scroll_y
        
        for i, planeta in enumerate(imperio.planetas):
            # (A função carregar_imagem_miniatura() precisa ser copiada para este arquivo)
            if not hasattr(planeta, 'imagem_miniatura_cache'): # Cache simples
                try:
                    img = pygame.image.load(planeta.imagem_path).convert_alpha()
                    planeta.imagem_miniatura_cache = pygame.transform.scale(img, (60, 60))
                except Exception as e:
                    placeholder = pygame.Surface((60, 60))
                    placeholder.fill(COLOR_CARD)
                    planeta.imagem_miniatura_cache = placeholder
            
            card_y_on_screen = y_offset_cartoes + i * (ALTURA_CARTAO_PLANETA + PADDING_CARTAO)
            
            if card_y_on_screen > ALTURA_TELA or card_y_on_screen + ALTURA_CARTAO_PLANETA < 0:
                continue

            card_rect = pygame.Rect(20, card_y_on_screen, LARGURA_TELA - 40, ALTURA_CARTAO_PLANETA)
            pygame.draw.rect(screen, COLOR_CARD, card_rect, border_radius=10)
            
            if planeta.imagem_miniatura_cache:
                screen.blit(planeta.imagem_miniatura_cache, (card_rect.x + 15, card_rect.y + (ALTURA_CARTAO_PLANETA - 60) // 2))

            text_x = card_rect.x + 90 
            draw_text(f"{planeta.nome} (Nível {planeta.nivel})", font_corpo, COLOR_WHITE, text_x, card_rect.y + 10)
            draw_text(f"Prod: {planeta.get_producao_por_segundo():.2f}/s", font_corpo, COLOR_GREEN, text_x, card_rect.y + 35)
            
            custo_str = f"Upar: {int(planeta.get_custo_upgrade())}"
            btn_rect = pygame.Rect(text_x, card_rect.y + 60, card_rect.width - 105, 30)
            pygame.draw.rect(screen, COLOR_BUTTON, btn_rect, border_radius=5)
            draw_text(custo_str, font_botao, COLOR_YELLOW, btn_rect.centerx, btn_rect.centery, anchor="center")
            
            if click_pos and btn_rect.collidepoint(click_pos):
                imperio.tentar_upar_planeta(i)
                click_pos = None
        
        screen.set_clip(None)

        # --- D. UI Fixa Inferior (Botão de Comprar) ---
        btn_comprar_rect = pygame.Rect(20, ALTURA_TELA - 60, LARGURA_TELA - 40, 50) 
        if imperio.ha_mais_planetas_para_comprar():
            pygame.draw.rect(screen, COLOR_BUTTON, btn_comprar_rect, border_radius=10)
            # ... (textos do botão de comprar) ...
            custo_planeta_str = f"Custo: {int(imperio.custo_proximo_planeta)}"
            draw_text(custo_planeta_str, font_botao, COLOR_YELLOW, btn_comprar_rect.centerx, btn_comprar_rect.centery + 5, anchor="center")
            nome_planeta_str = f"Colonizar {imperio.get_proximo_planeta_nome()}"
            draw_text(nome_planeta_str, font_botao_pequeno, COLOR_WHITE, btn_comprar_rect.centerx, btn_comprar_rect.centery - 10, anchor="center")
            
            if click_pos and btn_comprar_rect.collidepoint(click_pos):
                imperio.tentar_comprar_planeta()
                click_pos = None
        else:
            pygame.draw.rect(screen, COLOR_BUTTON_DISABLED, btn_comprar_rect, border_radius=10)
            draw_text("UNIVERSO CONQUISTADO!", font_botao, COLOR_GREEN, btn_comprar_rect.centerx, btn_comprar_rect.centery, anchor="center")

        pygame.display.flip()
        clock.tick(60)
    
    # Fim do loop do jogo, retorna para o gerenciador principal
    return

# --- Ponto de Entrada Principal ---
def main():
    """O Gerenciador de Estados principal do jogo."""
    
    usuario_logado = None
    
    while True: # Loop do Gerenciador (Login <-> Jogo)
        
        if not usuario_logado:
            pygame.display.set_caption("King of Planets 👑 - Login")
            usuario_logado = run_auth_screen(estado_inicial="LOGIN")
            
        if usuario_logado:
            pygame.display.set_caption(f"King of Planets 👑 - {usuario_logado}")
            run_game_loop(usuario_logado)
            
            # Quando run_game_loop termina (jogador fechou a janela do jogo),
            # nós resetamos o usuário e voltamos para a tela de login.
            usuario_logado = None 


if __name__ == "__main__":
    main()