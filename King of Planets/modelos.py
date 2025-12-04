import math
import pygame 
from planetas import DADOS_TERRA_MAE, LISTA_PLANETAS_COLONIZAVEIS

class Planeta:
    def __init__(self, dados_estaticos):
        self.nome = dados_estaticos["nome"]
        self.prod_base = dados_estaticos["prod_base"]
        self.custo_base_upgrade = dados_estaticos["custo_base_upgrade"]
        self.imagem_path = dados_estaticos["imagem_path"]
        self.historia = dados_estaticos.get("historia", "História não disponível.")
        
        self.nivel = 1
        self.multiplicador_custo = 1.5 
        
        self.missao_nivel_feita = False
        self.missao_meteoros_progresso = 0
        self.missao_meteoros_alvo = 3
        self.missao_meteoros_feita = False

        self.sprite = self.carregar_sprite()

    def carregar_sprite(self):
        try:
            img = pygame.image.load(self.imagem_path).convert_alpha()
            img = pygame.transform.scale(img, (200, 200))
            return img
        except Exception: return None 

    def get_producao_atual(self):
        return self.prod_base * self.nivel

    def get_custo_upgrade(self):
        return self.custo_base_upgrade * (self.multiplicador_custo ** (self.nivel - 1))

    def realizar_upgrade(self):
        self.nivel += 1

    def registrar_meteoro(self):
        """Chamado quando um meteoro é clicado neste planeta."""
        if not self.missao_meteoros_feita:
            self.missao_meteoros_progresso += 1
            if self.missao_meteoros_progresso >= self.missao_meteoros_alvo:
                self.missao_meteoros_feita = True
                return True 
        return False

    def verificar_missao_nivel(self):
        """Verifica se atingiu o nível 10."""
        if not self.missao_nivel_feita and self.nivel >= 10:
            self.missao_nivel_feita = True
            return True
        return False

class Imperio:
    def __init__(self):
        self.pontos_galaticos = 0.0
        self.moedas_galaticas = 0
        self.melhorias = {
            "auto_clicker": False,
            "chuva_meteoros": False
        }
        
        self.planetas_conquistados = [Planeta(DADOS_TERRA_MAE)]
        self.indice_proxima_colonizacao = 0 

    def get_producao_total_ps(self):
        total = 0
        for p in self.planetas_conquistados:
            total += p.get_producao_atual()
        return total

    def clicar_planeta(self, indice_planeta):
        if 0 <= indice_planeta < len(self.planetas_conquistados):
            planeta = self.planetas_conquistados[indice_planeta]
            ganho = max(1, planeta.get_producao_atual() * 0.1)
            self.pontos_galaticos += ganho
            return ganho
        return 0

    def tentar_upar_planeta(self, indice_planeta):
        if 0 <= indice_planeta < len(self.planetas_conquistados):
            planeta = self.planetas_conquistados[indice_planeta]
            custo = planeta.get_custo_upgrade()
            
            if self.pontos_galaticos >= custo:
                self.pontos_galaticos -= custo
                planeta.realizar_upgrade()
                
                if planeta.verificar_missao_nivel():
                    self.moedas_galaticas += 5
                    return "missao" 
                return True
        return False

    def registrar_clique_meteoro(self, indice_planeta):
        """Ganha pontos e verifica missão."""
        bonus = max(100, self.get_producao_total_ps() * 60)
        self.pontos_galaticos += bonus
        
        missao_completada = False
        if 0 <= indice_planeta < len(self.planetas_conquistados):
            if self.planetas_conquistados[indice_planeta].registrar_meteoro():
                self.moedas_galaticas += 5
                missao_completada = True
        
        return bonus, missao_completada

    def comprar_melhoria(self, tipo, custo):
        if self.moedas_galaticas >= custo and not self.melhorias.get(tipo, False):
            self.moedas_galaticas -= custo
            self.melhorias[tipo] = True
            return True
        return False

    def get_custo_proxima_colonizacao(self):
        if self.indice_proxima_colonizacao < len(LISTA_PLANETAS_COLONIZAVEIS):
            prox_dados = LISTA_PLANETAS_COLONIZAVEIS[self.indice_proxima_colonizacao]
            return prox_dados["custo_base_upgrade"] * 5 
        return None 

    def tentar_colonizar_novo(self):
        custo = self.get_custo_proxima_colonizacao()
        if custo is not None and self.pontos_galaticos >= custo:
            self.pontos_galaticos -= custo
            
            dados_novo = LISTA_PLANETAS_COLONIZAVEIS[self.indice_proxima_colonizacao]
            novo_planeta = Planeta(dados_novo)
            
            self.planetas_conquistados.append(novo_planeta)
            self.indice_proxima_colonizacao += 1
            return True
        return False