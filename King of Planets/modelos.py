import math
# Importa os dados dos nossos novos planetas
import planetas

class Planeta:
    """
    Representa um único planeta no império.
    """
    def __init__(self, nome, producao_base, custo_base, imagem_path):
        self.nome = nome
        self.nivel = 1
        self.producao_base = producao_base
        self.custo_base = custo_base
        self.multiplicador_custo = 1.15
        self.imagem_path = imagem_path
        self.imagem_miniatura_cache = None # Cache de runtime, não salvo

    def get_producao_por_segundo(self):
        return self.producao_base * self.nivel

    def get_custo_upgrade(self):
        return self.custo_base * (self.multiplicador_custo ** self.nivel)

    def upar(self):
        self.nivel += 1

    # --- NOVO MÉTODO PARA SALVAR ---
    def to_dict(self):
        """Converte o estado do planeta para um dicionário salvável."""
        return {
            "nome": self.nome,
            "nivel": self.nivel,
            "producao_base": self.producao_base,
            "custo_base": self.custo_base,
            "imagem_path": self.imagem_path
        }

    # --- NOVO MÉTODO PARA CARREGAR ---
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de Planeta a partir de um dicionário salvo."""
        # Cria um planeta novo com os dados base
        planeta = cls(
            data["nome"], 
            data["producao_base"], 
            data["custo_base"], 
            data["imagem_path"]
        )
        # Restaura o progresso (nível)
        planeta.nivel = data["nivel"]
        return planeta

class Imperio:
    """
    Representa o jogador, gerenciando os pontos e os planetas.
    """
    def __init__(self):
        self.pontos_galaticos = 0.0
        self.planetas = []
        self.custo_proximo_planeta = 1000 
        
        # Adiciona o planeta inicial APENAS se a lista estiver vazia
        # (Isso evita adicionar Terra-Mãe duplicada ao carregar um save)
        if not self.planetas:
            dados_terra = planetas.DADOS_TERRA_MAE
            self.planetas.append(Planeta(
                dados_terra["nome"], 
                dados_terra["prod_base"], 
                dados_terra["custo_base_upgrade"],
                dados_terra["imagem_path"]
            ))
        
        self.proximo_planeta_index = 0

    # ... (get_producao_total_ps, produzir_recursos_intervalo, clicar_planeta, etc...) ...
    def get_producao_total_ps(self):
        return sum(p.get_producao_por_segundo() for p in self.planetas)

    def produzir_recursos_intervalo(self, intervalo_segundos):
        producao_total_ps = self.get_producao_total_ps()
        ganhos = producao_total_ps * intervalo_segundos
        if ganhos > 0:
            self.pontos_galaticos += ganhos
            return ganhos
        return 0

    def clicar_planeta(self):
        pontos_por_clique = self.get_producao_total_ps()
        if pontos_por_clique < 1:
            pontos_por_clique = 1
        self.pontos_galaticos += pontos_por_clique
        return pontos_por_clique

    def tentar_upar_planeta(self, indice_planeta):
        # ... (sem mudanças) ...
        if 0 <= indice_planeta < len(self.planetas):
            planeta = self.planetas[indice_planeta]
            custo = planeta.get_custo_upgrade()
            if self.pontos_galaticos >= custo:
                self.pontos_galaticos -= custo
                planeta.upar()
                return True
        return False
    
    def ha_mais_planetas_para_comprar(self):
        # ... (sem mudanças) ...
        return self.proximo_planeta_index < len(planetas.LISTA_PLANETAS_COLONIZAVEIS)

    def get_proximo_planeta_nome(self):
        # ... (sem mudanças) ...
        if self.ha_mais_planetas_para_comprar():
            return planetas.LISTA_PLANETAS_COLONIZAVEIS[self.proximo_planeta_index]["nome"]
        return ""

    def tentar_comprar_planeta(self):
        # ... (sem mudanças) ...
        if not self.ha_mais_planetas_para_comprar():
            return False
        if self.pontos_galaticos >= self.custo_proximo_planeta:
            dados_planeta = planetas.LISTA_PLANETAS_COLONIZAVEIS[self.proximo_planeta_index]
            self.pontos_galaticos -= self.custo_proximo_planeta
            self.planetas.append(Planeta(
                dados_planeta["nome"], 
                dados_planeta["prod_base"], 
                dados_planeta["custo_base_upgrade"],
                dados_planeta["imagem_path"]
            ))
            self.proximo_planeta_index += 1
            self.custo_proximo_planeta *= 3.5 
            return True
        return False

    # --- NOVO MÉTODO PARA SALVAR ---
    def to_dict(self):
        """Converte o estado do império para um dicionário salvável."""
        return {
            "pontos_galaticos": self.pontos_galaticos,
            "custo_proximo_planeta": self.custo_proximo_planeta,
            "proximo_planeta_index": self.proximo_planeta_index,
            "planetas": [p.to_dict() for p in self.planetas] # Salva cada planeta
        }

    # --- NOVO MÉTODO PARA CARREGAR ---
    @classmethod
    def from_dict(cls, data):
        """Cria uma instância de Imperio a partir de dados salvos."""
        # Cria um império "vazio"
        imperio = cls()
        
        # Limpa a lista (o __init__ padrão adiciona a Terra-Mãe)
        imperio.planetas = []

        # Restaura o estado salvo
        imperio.pontos_galaticos = data.get("pontos_galaticos", 0)
        imperio.custo_proximo_planeta = data.get("custo_proximo_planeta", 1000)
        imperio.proximo_planeta_index = data.get("proximo_planeta_index", 0)
        
        # Reconstrói os planetas a partir dos dados salvos
        planetas_data = data.get("planetas", [])
        for planeta_data in planetas_data:
            imperio.planetas.append(Planeta.from_dict(planeta_data))
            
        return imperio