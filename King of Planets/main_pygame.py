import pygame
import sys
import os
import wave
import math
import struct
import random

# Módulos do Jogo
from modelos import Imperio
from visuals import GerenciadorDeEfeitos, Starfield
from usuarios import registrar_usuario, login_usuario
# --- NOVO: Importa as telas de loja e missões ---
from loja_e_missoes import desenhar_icone_missoes, desenhar_icone_loja, desenhar_popup_missoes, desenhar_popup_loja

# Importando TUDO de utils
from utils import (
    formatar_numero_jogo,
    COLOR_BG, COLOR_WHITE, COLOR_BUTTON, COLOR_BUTTON_DISABLED,
    COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW, COLOR_RED,
    COLOR_INPUT_ACTIVE, COLOR_INPUT_INACTIVE, COLOR_PONTOS_RGB
)

# --- Define COLOR_CARD caso não exista no utils ---
try:
    from utils import COLOR_CARD
except ImportError:
    COLOR_CARD = (30, 30, 50)

# --- Configurações Iniciais ---
pygame.init()
pygame.font.init()

# Inicializa o Mixer com configurações robustas
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print(f"AVISO: Não foi possível iniciar o sistema de som: {e}")

# --- Constantes da Janela ---
LARGURA_TELA = 400
ALTURA_TELA = 600
screen = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
clock = pygame.time.Clock()

# --- Fontes ---
font_titulo = pygame.font.SysFont("Arial", 32, bold=True)
font_padrao = pygame.font.SysFont("Arial", 20)
font_botao = pygame.font.SysFont("Arial", 18, bold=True)
font_botao_pequeno = pygame.font.SysFont("Arial", 14)
font_pontos = pygame.font.SysFont("Consolas", 28, bold=True)
font_input = pygame.font.SysFont("Consolas", 22)
font_mini = pygame.font.SysFont("Arial", 12)
# --- ADICIONADO: Fonte para a história ---
font_historia = pygame.font.SysFont("Georgia", 18, italic=True)

# ==============================================================================
# SISTEMA DE GERAÇÃO DE SOM AUTOMÁTICO (EMBUTIDO)
# ==============================================================================
def salvar_wav(nome_arquivo, dados):
    """Salva dados de áudio cru em um arquivo .wav"""
    caminho_completo = os.path.join(os.path.dirname(__file__), nome_arquivo)
    try:
        with wave.open(caminho_completo, 'w') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100)
            for sample in dados:
                sample = max(-1.0, min(1.0, sample))
                f.writeframes(struct.pack('<h', int(sample * 32767.0)))
    except Exception as e:
        print(f"[ERRO] Falha ao salvar wav: {e}")

def gerar_onda(freq, duracao, vol=0.5):
    """Gera onda senoidal simples"""
    audio = []
    num_samples = int(duracao * 44100)
    for i in range(num_samples):
        t = float(i) / 44100
        val = math.sin(2 * math.pi * freq * t)
        envelope = 1.0 - (i / num_samples) # Fade out
        audio.append(val * vol * envelope)
    return audio

def garantir_sons_existem():
    """Verifica se os sons existem. Se não, cria eles agora."""
    base_dir = os.path.dirname(__file__)
    
    if not os.path.exists(os.path.join(base_dir, "sfx_click.wav")):
        salvar_wav("sfx_click.wav", gerar_onda(800, 0.1, 0.6))

    if not os.path.exists(os.path.join(base_dir, "sfx_upgrade.wav")):
        audio = []
        for i in range(int(0.4 * 44100)):
            t = i / 44100
            freq = 400 + (800 * t)
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0 
            audio.append(val * 0.3 * (1 - t/0.4))
        salvar_wav("sfx_upgrade.wav", audio)

    if not os.path.exists(os.path.join(base_dir, "sfx_colonizar.wav")):
        n1 = gerar_onda(261.63, 1.5, 0.3) # C
        n2 = gerar_onda(329.63, 1.5, 0.3) # E
        n3 = gerar_onda(392.00, 1.5, 0.3) # G
        mix = [sum(x) for x in zip(n1, n2, n3)]
        salvar_wav("sfx_colonizar.wav", mix)
        
    # Som de Missão Cumprida (Novo)
    if not os.path.exists(os.path.join(base_dir, "sfx_mission.wav")):
        salvar_wav("sfx_mission.wav", gerar_onda(1200, 0.2, 0.4))

# ==============================================================================
# CLASSE DE SOM
# ==============================================================================
class SistemaDeSomInterno:
    def __init__(self):
        self.sons = {}
        garantir_sons_existem()
        base_dir = os.path.dirname(__file__)
        self.carregar("click", os.path.join(base_dir, "sfx_click.wav"), 0.3)
        self.carregar("upgrade", os.path.join(base_dir, "sfx_upgrade.wav"), 0.4)
        self.carregar("colonizar", os.path.join(base_dir, "sfx_colonizar.wav"), 0.5)
        self.carregar("mission", os.path.join(base_dir, "sfx_mission.wav"), 0.5)

    def carregar(self, nome, caminho, vol):
        if os.path.exists(caminho):
            try:
                som = pygame.mixer.Sound(caminho)
                som.set_volume(vol)
                self.sons[nome] = som
            except Exception as e:
                print(f"[ERRO] Falha ao carregar {nome}: {e}")

    def play(self, nome):
        if nome in self.sons: self.sons[nome].play()
        
    # Mantive para compatibilidade
    def play_click(self): self.play("click")
    def play_upgrade(self): self.play("upgrade")
    def play_colonizar(self): self.play("colonizar")

# ==============================================================================
# NOVA CLASSE: METEORO BÔNUS
# ==============================================================================
class MeteoroBonus:
    # Adicionei delay para suportar a "chuva de meteoros"
    def __init__(self, largura_tela, altura_tela, delay=0):
        self.largura = largura_tela
        self.altura = altura_tela
        self.x = -100
        self.y = -100
        self.vx = 0
        self.vy = 0
        self.raio = 30
        self.ativo = False
        self.delay_spawn = delay
        self.cor_nucleo = (255, 255, 100) # Amarelo
        self.cor_cauda = (255, 100, 50)   # Laranja avermelhado
        self.rect = pygame.Rect(0,0,0,0)

    def spawn(self):
        """Nasce em um lado e vai para o outro"""
        lado = random.choice([-1, 1]) # -1 Esquerda, 1 Direita
        if lado == -1:
            self.x = -50
            self.vx = random.uniform(200, 450) # Velocidade para direita
        else:
            self.x = self.largura + 50
            self.vx = random.uniform(-450, -200) # Velocidade para esquerda
        
        self.y = random.randint(100, self.altura - 200) # Altura variada
        self.vy = random.uniform(-50, 50) # Leve variação vertical
        self.ativo = True
        self.atualizar_rect()

    def update(self, dt):
        # Lógica de atraso para chuva de meteoros
        if self.delay_spawn > 0:
            self.delay_spawn -= dt
            if self.delay_spawn <= 0:
                self.spawn()
            return

        if not self.ativo: return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.atualizar_rect()

        # Verifica se saiu da tela
        if (self.vx > 0 and self.x > self.largura + 60) or \
           (self.vx < 0 and self.x < -60):
            self.ativo = False

    def atualizar_rect(self):
        self.rect = pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio*2, self.raio*2)

    def check_click(self, pos):
        if not self.ativo: return False
        # Colisão circular simples
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distancia_sq = dx*dx + dy*dy
        if distancia_sq < self.raio * self.raio:
            self.ativo = False
            return True
        return False

    def draw(self, screen):
        # Só desenha se estiver ativo
        if not self.ativo: return
        # Desenha "cauda" (circulo maior atrás)
        pygame.draw.circle(screen, self.cor_cauda, (int(self.x - self.vx*0.05), int(self.y)), self.raio + 5)
        # Desenha núcleo
        pygame.draw.circle(screen, self.cor_nucleo, (int(self.x), int(self.y)), self.raio)


# --- Funções Gráficas ---
def draw_text(text, font, color, x, y, anchor="topleft"):
    surface = font.render(str(text), True, color)
    rect = surface.get_rect()
    if anchor == "center": rect.center = (x, y)
    elif anchor == "topleft": rect.topleft = (x, y)
    screen.blit(surface, rect)

# --- ADICIONADO: Função para quebrar texto ---
def draw_multiline_text(surface, text, font, color, rect):
    words = text.split(' ')
    space = font.size(' ')[0]  
    max_width = rect.width
    x, y = rect.topleft
    
    line = []
    for word in words:
        word_surface = font.render(word, True, color)
        line_width = font.size(' '.join(line + [word]))[0]
        
        if line_width > max_width:
            surface.blit(font.render(' '.join(line), True, color), (x, y))
            y += font.get_height() + 5
            line = [word]
        else:
            line.append(word)
            
    surface.blit(font.render(' '.join(line), True, color), (x, y))

# --- Tela de Autenticação ---
def run_auth_screen(estado_inicial="LOGIN"):
    username_text = ""; password_text = ""; active_input = None 
    mensagem_erro = ""; mensagem_sucesso = ""
    input_user_rect = pygame.Rect(50, 200, 300, 40)
    input_pass_rect = pygame.Rect(50, 280, 300, 40)
    btn_action_rect = pygame.Rect(100, 350, 200, 50)
    btn_switch_rect = pygame.Rect(50, 420, 300, 30)

    while True:
        screen.fill(COLOR_BG)
        titulo = "LOGIN" if estado_inicial == "LOGIN" else "REGISTRO"
        draw_text(titulo, font_titulo, COLOR_WHITE, LARGURA_TELA // 2, 100, anchor="center")

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_user_rect.collidepoint(event.pos): active_input = "username"
                elif input_pass_rect.collidepoint(event.pos): active_input = "password"
                else: active_input = None
                
                if btn_action_rect.collidepoint(event.pos):
                    if estado_inicial == "LOGIN":
                        sucesso, msg = login_usuario(username_text, password_text)
                        if sucesso: return username_text 
                        else: mensagem_erro = msg
                    else: 
                        sucesso, msg = registrar_usuario(username_text, password_text)
                        if sucesso: mensagem_sucesso = msg; mensagem_erro = ""; estado_inicial = "LOGIN" 
                        else: mensagem_erro = msg

                if btn_switch_rect.collidepoint(event.pos):
                    estado_inicial = "REGISTRO" if estado_inicial == "LOGIN" else "LOGIN"
                    mensagem_erro = ""; mensagem_sucesso = ""

            if event.type == pygame.KEYDOWN:
                if active_input == "username":
                    if event.key == pygame.K_BACKSPACE: username_text = username_text[:-1]
                    else: username_text += event.unicode
                elif active_input == "password":
                    if event.key == pygame.K_BACKSPACE: password_text = password_text[:-1]
                    else: password_text += event.unicode

        color_input_user = COLOR_INPUT_ACTIVE if active_input == "username" else COLOR_INPUT_INACTIVE
        color_input_pass = COLOR_INPUT_ACTIVE if active_input == "password" else COLOR_INPUT_INACTIVE

        draw_text("Usuário:", font_botao, COLOR_WHITE, 50, 180)
        draw_text("Senha:", font_botao, COLOR_WHITE, 50, 260)
        mostrar_cursor = (pygame.time.get_ticks() // 500) % 2 == 0

        pygame.draw.rect(screen, color_input_user, input_user_rect, border_radius=5)
        txt_usr = username_text + ("|" if active_input == "username" and mostrar_cursor else "")
        screen.blit(font_input.render(txt_usr, True, COLOR_WHITE), (input_user_rect.x + 10, input_user_rect.y + 10))

        pygame.draw.rect(screen, color_input_pass, input_pass_rect, border_radius=5)
        txt_pass = ("*" * len(password_text)) + ("|" if active_input == "password" and mostrar_cursor else "")
        screen.blit(font_input.render(txt_pass, True, COLOR_WHITE), (input_pass_rect.x + 10, input_pass_rect.y + 10))

        pygame.draw.rect(screen, COLOR_BUTTON, btn_action_rect, border_radius=10)
        draw_text("ENTRAR" if estado_inicial == "LOGIN" else "CRIAR CONTA", font_botao, COLOR_WHITE, btn_action_rect.centerx, btn_action_rect.centery, anchor="center")
        draw_text("Não tem conta? Registre-se" if estado_inicial == "LOGIN" else "Já tem conta? Faça Login", font_botao_pequeno, COLOR_BLUE, btn_switch_rect.centerx, btn_switch_rect.centery, anchor="center")

        if mensagem_erro: draw_text(mensagem_erro, font_botao_pequeno, COLOR_RED, LARGURA_TELA//2, 460, anchor="center")
        if mensagem_sucesso: draw_text(mensagem_sucesso, font_botao_pequeno, COLOR_GREEN, LARGURA_TELA//2, 460, anchor="center")

        pygame.display.flip()
        clock.tick(30)


# --- Tela do Jogo Principal ---
def run_game(usuario):
    imperio = Imperio()
    efeitos = GerenciadorDeEfeitos()
    starfield = Starfield(LARGURA_TELA, ALTURA_TELA)
    sons = SistemaDeSomInterno()
    
    # --- ALTERADO: Lista de Meteoros (para suportar chuva) ---
    meteoros = [] 
    tempo_ate_proximo_meteoro = random.uniform(15, 45)
    tempo_passado_meteoro = 0

    running = True
    indice_visualizacao = 0 
    escala_animacao = 1.0 
    
    # --- Variáveis Novas ---
    tempo_auto_click = 0 # Timer para o auto clicker
    mostrando_missoes = False # Estado popup missões
    mostrando_loja = False # Estado popup loja

    # --- VARIÁVEIS DA HISTÓRIA (Lore) ---
    mostrando_historia = False
    historia_planeta = None
    texto_atual_digitado = ""
    indice_letra = 0
    tempo_digitacao = 0
    velocidade_digitacao = 0.03
    rect_historia_bg = pygame.Rect(20, 150, LARGURA_TELA - 40, 300)

    area_planeta_rect = pygame.Rect(0, 120, LARGURA_TELA, 280)
    btn_upgrade_rect = pygame.Rect(50, 480, 300, 60)
    btn_esq_rect = pygame.Rect(10, 250, 40, 40)
    btn_dir_rect = pygame.Rect(LARGURA_TELA - 50, 250, 40, 40)

    while running:
        dt = clock.get_time() / 1000 
        escala_animacao += (1.0 - escala_animacao) * 10 * dt
        
        producao_frame = imperio.get_producao_total_ps() * dt
        if producao_frame > 0:
            imperio.pontos_galaticos += producao_frame
        
        starfield.update()

        # --- LÓGICA AUTO CLICKER (20 clicks/s = 0.05s) ---
        if imperio.melhorias["auto_clicker"]:
            tempo_auto_click += dt
            if tempo_auto_click >= 0.05:
                # Clica automaticamente no planeta atual (sem efeito visual pra não poluir)
                if indice_visualizacao < len(imperio.planetas_conquistados):
                    imperio.clicar_planeta(indice_visualizacao)
                tempo_auto_click = 0

        # --- LÓGICA DE METEOROS (LISTA) ---
        if not mostrando_historia and not mostrando_missoes and not mostrando_loja:
            tempo_passado_meteoro += dt
            if tempo_passado_meteoro >= tempo_ate_proximo_meteoro:
                # Se tiver a melhoria, spawna 4 (chuva), senão 1
                qtd = 4 if imperio.melhorias["chuva_meteoros"] else 1
                for i in range(qtd):
                    # Pequeno delay entre eles na chuva
                    atraso = i * 0.3
                    novo = MeteoroBonus(LARGURA_TELA, ALTURA_TELA, delay=atraso)
                    if i == 0: novo.spawn() # O primeiro já ativa
                    meteoros.append(novo)
                
                tempo_passado_meteoro = 0
                tempo_ate_proximo_meteoro = random.uniform(15, 45)
            
            # Atualiza lista e remove inativos
            for m in meteoros: m.update(dt)
            meteoros = [m for m in meteoros if m.ativo or m.delay_spawn > 0]

        # Eventos
        click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False; pygame.quit(); sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_pos = event.pos

                # --- 1. POPUPS E MODAIS (Bloqueantes) ---
                if mostrando_historia:
                    txt = getattr(historia_planeta, "historia", "...")
                    if indice_letra < len(txt):
                        texto_atual_digitado = txt; indice_letra = len(txt)
                    else:
                        mostrando_historia = False; indice_visualizacao = len(imperio.planetas_conquistados) - 1
                    continue
                
                if mostrando_missoes:
                    mostrando_missoes = False # Clique fecha
                    continue

                if mostrando_loja:
                    # Verifica clique nos botões da loja
                    # Pegamos os rects chamando a função de desenho (hack simples para sync)
                    r1, r2 = desenhar_popup_loja(screen, LARGURA_TELA, ALTURA_TELA, imperio) 
                    # Na verdade precisamos recalcular pois não estamos desenhando agora,
                    # mas como a posição é fixa no loja_e_missoes.py, podemos testar:
                    # Item 1: y=180, Item 2: y=260 (baseado no rect da janela 80+100 e 80+180)
                    rect_btn1 = pygame.Rect(60, 180, LARGURA_TELA - 120, 60)
                    rect_btn2 = pygame.Rect(60, 260, LARGURA_TELA - 120, 60)

                    if rect_btn1.collidepoint(click_pos):
                        if imperio.comprar_melhoria("auto_clicker", 25): sons.play("upgrade")
                    elif rect_btn2.collidepoint(click_pos):
                        if imperio.comprar_melhoria("chuva_meteoros", 30): sons.play("upgrade")
                    else:
                        mostrando_loja = False # Clicou fora
                    continue

                # --- 2. JOGO NORMAL ---
                
                # Botões de UI (Estrela e Loja)
                rect_missoes = desenhar_icone_missoes(screen, 10, 60)
                if rect_missoes.collidepoint(click_pos):
                    mostrando_missoes = True
                    continue
                
                # Loja (só se estiver vendo planeta)
                if indice_visualizacao < len(imperio.planetas_conquistados):
                    rect_loja = desenhar_icone_loja(screen, LARGURA_TELA//2 - 25, 440)
                    if rect_loja.collidepoint(click_pos):
                        mostrando_loja = True
                        continue

                # CLIQUE NOS METEOROS (Lista)
                hit_meteoro = False
                for m in meteoros:
                    if m.check_click(click_pos):
                        bonus, missao_ok = imperio.registrar_clique_meteoro(indice_visualizacao)
                        efeitos.spawn_click_effect(f"+{formatar_numero_jogo(bonus)}", click_pos[0], click_pos[1])
                        sons.play("colonizar")
                        if missao_ok: 
                            efeitos.spawn_click_effect("MISSÃO!", click_pos[0], click_pos[1]-30)
                            sons.play("mission")
                        hit_meteoro = True
                        break # Clica um por vez
                if hit_meteoro: continue
                
                if click_pos:
                    # 1. Farmar
                    if area_planeta_rect.collidepoint(click_pos):
                        if indice_visualizacao < len(imperio.planetas_conquistados):
                            ganho = imperio.clicar_planeta(indice_visualizacao)
                            efeitos.spawn_click_effect(ganho, click_pos[0], click_pos[1])
                            escala_animacao = 0.9
                            sons.play_click()

                    # 2. Navegação
                    if btn_esq_rect.collidepoint(click_pos):
                        if indice_visualizacao > 0: indice_visualizacao -= 1

                    if btn_dir_rect.collidepoint(click_pos):
                        max_idx = len(imperio.planetas_conquistados)
                        if imperio.get_custo_proxima_colonizacao() is not None:
                             if indice_visualizacao < max_idx: indice_visualizacao += 1
                        else:
                             if indice_visualizacao < max_idx - 1: indice_visualizacao += 1

                    # 3. Upgrade / Colonizar
                    if btn_upgrade_rect.collidepoint(click_pos):
                        if indice_visualizacao < len(imperio.planetas_conquistados):
                            res = imperio.tentar_upar_planeta(indice_visualizacao)
                            if res:
                                efeitos.spawn_click_effect("LEVEL UP!", btn_upgrade_rect.centerx, btn_upgrade_rect.y)
                                sons.play("upgrade")
                                if res == "missao":
                                    efeitos.spawn_click_effect("MISSÃO!", btn_upgrade_rect.centerx, btn_upgrade_rect.y-30)
                                    sons.play("mission")

                        elif indice_visualizacao == len(imperio.planetas_conquistados):
                            if imperio.tentar_colonizar_novo():
                                sons.play("colonizar")
                                # --- GATILHO DA HISTÓRIA ---
                                mostrando_historia = True
                                historia_planeta = imperio.planetas_conquistados[-1]
                                texto_atual_digitado = ""
                                indice_letra = 0
                                tempo_digitacao = 0
                                # ---------------------------

        # --- Desenho ---
        screen.fill(COLOR_BG)
        starfield.draw(screen)
        
        # Desenha meteoros
        for m in meteoros: m.draw(screen)

        draw_text(f"Império de {usuario}", font_padrao, COLOR_WHITE, 10, 10)
        texto_pontos = f"Pontos: {formatar_numero_jogo(imperio.pontos_galaticos)}"
        draw_text(texto_pontos, font_pontos, COLOR_PONTOS_RGB, LARGURA_TELA // 2, 50, anchor="center")
        
        prod_total = formatar_numero_jogo(imperio.get_producao_total_ps())
        draw_text(f"Produção Total: {prod_total}/s", font_botao_pequeno, COLOR_GREEN, LARGURA_TELA // 2, 80, anchor="center")

        # UI DE MOEDAS (Canto Direito)
        txt_m = font_padrao.render(f"Moedas: {imperio.moedas_galaticas}", True, COLOR_YELLOW)
        screen.blit(txt_m, (LARGURA_TELA - txt_m.get_width() - 10, 10))

        # ÍCONE MISSÕES
        desenhar_icone_missoes(screen, 10, 60)

        vendo_planeta_existente = indice_visualizacao < len(imperio.planetas_conquistados)
        
        if vendo_planeta_existente:
            planeta_atual = imperio.planetas_conquistados[indice_visualizacao]
            
            draw_text(f"{planeta_atual.nome}", font_titulo, COLOR_WHITE, LARGURA_TELA//2, 130, anchor="center")
            draw_text(f"Nível {planeta_atual.nivel}", font_padrao, COLOR_BLUE, LARGURA_TELA//2, 165, anchor="center")
            
            if planeta_atual.sprite:
                img = planeta_atual.sprite
                largura_nova = int(img.get_width() * escala_animacao)
                altura_nova = int(img.get_height() * escala_animacao)
                img_animada = pygame.transform.scale(img, (largura_nova, altura_nova))
                rect_img = img_animada.get_rect(); rect_img.center = area_planeta_rect.center
                screen.blit(img_animada, rect_img)
            else:
                raio_animado = int(90 * escala_animacao)
                pygame.draw.circle(screen, (50, 100, 200), area_planeta_rect.center, raio_animado)
                draw_text("🌍", pygame.font.SysFont("Segoe UI Emoji", int(100 * escala_animacao)), COLOR_WHITE, area_planeta_rect.centerx, area_planeta_rect.centery, anchor="center")
            
            prod_ind = formatar_numero_jogo(planeta_atual.get_producao_atual())
            draw_text(f"+{prod_ind}/s", font_botao, COLOR_GREEN, LARGURA_TELA//2, 380, anchor="center")

            # Botão Upgrade
            custo_up = planeta_atual.get_custo_upgrade()
            pode_pagar = imperio.pontos_galaticos >= custo_up
            cor_btn = COLOR_BUTTON if pode_pagar else COLOR_BUTTON_DISABLED
            pygame.draw.rect(screen, cor_btn, btn_upgrade_rect, border_radius=10)
            draw_text("UPGRADE PLANETA", font_botao, COLOR_WHITE, btn_upgrade_rect.centerx, btn_upgrade_rect.centery - 10, anchor="center")
            draw_text(f"Custo: {formatar_numero_jogo(custo_up)}", font_botao_pequeno, COLOR_YELLOW, btn_upgrade_rect.centerx, btn_upgrade_rect.centery + 15, anchor="center")

            # ÍCONE LOJA
            desenhar_icone_loja(screen, LARGURA_TELA//2 - 25, 440)

            # Barra Rodapé
            custo_colonia = imperio.get_custo_proxima_colonizacao()
            if custo_colonia is not None:
                porc = imperio.pontos_galaticos / custo_colonia
                if porc > 1.0: porc = 1.0
                rect_bg_bar = pygame.Rect(50, 560, 300, 10)
                rect_fg_bar = pygame.Rect(50, 560, int(300 * porc), 10)
                pygame.draw.rect(screen, (40,40,60), rect_bg_bar, border_radius=5)
                cor_progresso = COLOR_GREEN if porc >= 1.0 else COLOR_YELLOW
                pygame.draw.rect(screen, cor_progresso, rect_fg_bar, border_radius=5)
                draw_text(f"Próxima Conquista: {int(porc*100)}%", font_mini, (150,150,150), LARGURA_TELA//2, 550, anchor="center")

        else:
            custo_colonia = imperio.get_custo_proxima_colonizacao()
            draw_text("Espaço Não Explorado", font_titulo, COLOR_WHITE, LARGURA_TELA//2, 130, anchor="center")
            pygame.draw.circle(screen, (50, 50, 50), area_planeta_rect.center, 70, width=5)
            draw_text("?", font_titulo, (100,100,100), area_planeta_rect.centerx, area_planeta_rect.centery, anchor="center")

            if custo_colonia is not None:
                porc = imperio.pontos_galaticos / custo_colonia
                if porc > 1.0: porc = 1.0
                largura_barra = 250; altura_barra = 20
                x_barra = (LARGURA_TELA - largura_barra) // 2
                y_barra = 350
                pygame.draw.rect(screen, (40, 40, 60), (x_barra, y_barra, largura_barra, altura_barra), border_radius=10)
                if porc > 0:
                    pygame.draw.rect(screen, COLOR_GREEN if porc >= 1 else COLOR_YELLOW, (x_barra, y_barra, int(largura_barra*porc), altura_barra), border_radius=10)
                draw_text(f"{int(porc * 100)}%", font_botao_pequeno, COLOR_WHITE, x_barra + largura_barra/2, y_barra + 10, anchor="center")

                pode_pagar = imperio.pontos_galaticos >= custo_colonia
                cor_btn = COLOR_BUTTON if pode_pagar else COLOR_BUTTON_DISABLED
                pygame.draw.rect(screen, cor_btn, btn_upgrade_rect, border_radius=10)
                draw_text("COLONIZAR NOVO", font_botao, COLOR_WHITE, btn_upgrade_rect.centerx, btn_upgrade_rect.centery - 10, anchor="center")
                draw_text(f"Custo: {formatar_numero_jogo(custo_colonia)}", font_botao_pequeno, COLOR_YELLOW, btn_upgrade_rect.centerx, btn_upgrade_rect.centery + 15, anchor="center")
            else:
                draw_text("UNIVERSO DOMINADO!", font_titulo, COLOR_GREEN, LARGURA_TELA//2, 400, anchor="center")

        if indice_visualizacao > 0:
            pygame.draw.rect(screen, COLOR_BUTTON, btn_esq_rect, border_radius=5)
            draw_text("<", font_titulo, COLOR_WHITE, btn_esq_rect.centerx, btn_esq_rect.centery, anchor="center")
        max_idx = len(imperio.planetas_conquistados)
        if (indice_visualizacao < max_idx and imperio.get_custo_proxima_colonizacao() is not None) or (indice_visualizacao < max_idx - 1):
             pygame.draw.rect(screen, COLOR_BUTTON, btn_dir_rect, border_radius=5)
             draw_text(">", font_titulo, COLOR_WHITE, btn_dir_rect.centerx, btn_dir_rect.centery, anchor="center")

        efeitos.update_e_desenha(screen, dt)

        # --- DESENHO DO OVERLAY DE HISTÓRIA ---
        if mostrando_historia and historia_planeta:
            overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA))
            overlay.set_alpha(200)
            overlay.fill((0,0,0))
            screen.blit(overlay, (0,0))

            pygame.draw.rect(screen, COLOR_CARD, rect_historia_bg, border_radius=15)
            pygame.draw.rect(screen, COLOR_WHITE, rect_historia_bg, width=2, border_radius=15)

            # Lógica da Máquina de Escrever
            texto_completo = getattr(historia_planeta, "historia", "História não disponível.")
            if indice_letra < len(texto_completo):
                tempo_digitacao += dt
                if tempo_digitacao >= velocidade_digitacao:
                    tempo_digitacao = 0
                    texto_atual_digitado += texto_completo[indice_letra]
                    indice_letra += 1
            
            draw_text("NOVA CONQUISTA!", font_titulo, COLOR_YELLOW, LARGURA_TELA//2, 170, anchor="center")
            draw_text(historia_planeta.nome, font_padrao, COLOR_BLUE, LARGURA_TELA//2, 210, anchor="center")
            
            rect_texto = pygame.Rect(rect_historia_bg.x + 20, rect_historia_bg.y + 80, rect_historia_bg.width - 40, rect_historia_bg.height - 100)
            draw_multiline_text(screen, texto_atual_digitado, font_historia, COLOR_WHITE, rect_texto)

            if indice_letra >= len(texto_completo):
                if (pygame.time.get_ticks() // 500) % 2 == 0:
                    draw_text("- Clique para Continuar -", font_botao_pequeno, (150, 150, 150), LARGURA_TELA//2, 430, anchor="center")
        
        # --- DESENHO POPUPS (Loja e Missões) ---
        if mostrando_missoes and vendo_planeta_existente:
            desenhar_popup_missoes(screen, LARGURA_TELA, ALTURA_TELA, imperio.planetas_conquistados[indice_visualizacao])
        
        if mostrando_loja:
            desenhar_popup_loja(screen, LARGURA_TELA, ALTURA_TELA, imperio)

        pygame.display.flip()
        clock.tick(60)
    return

def main():
    usuario_logado = None
    while True: 
        if not usuario_logado:
            pygame.display.set_caption("King of Planets 👑 - Login")
            usuario_logado = run_auth_screen(estado_inicial="LOGIN")
        if usuario_logado:
            pygame.display.set_caption(f"King of Planets 👑 - {usuario_logado}")
            run_game(usuario_logado)
            break

if __name__ == "__main__":
    try: main()
    except Exception as e:
        import traceback; print("\nERRO FATAL:"); traceback.print_exc(); input("Enter para fechar...")