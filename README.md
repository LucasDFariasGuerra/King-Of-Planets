## 👑King of Planets
Um jogo idle tycoon espacial feito em Python e Pygame, onde seu objetivo é clicar, evoluir e colonizar planetas para se tornar o Rei do Universo.

## Sobre o Jogo
King of Planets é um jogo incremental (ou idle) com uma mecânica de clicker. Você começa com um único planeta, a "Terra-Mãe", e deve clicar para gerar seus primeiros Pontos Galáticos.

Use esses pontos para melhorar seu planeta, aumentando sua produção passiva. Quando tiver o suficiente, você poderá colonizar novos planetas do sistema solar e além, cada um com sua própria imagem, taxa de produção e custo de upgrade.

O jogo salva seu progresso, permitindo que você feche o jogo e continue sua conquista universal exatamente de onde parou.

## Features Principais
O projeto, em seu estado atual, inclui:

Sistema de Jogo Idle: Planetas geram Pontos Galáticos passivamente, mesmo enquanto você apenas observa.

Mecânica de Clicker: Clique no planeta principal (Terra-Mãe) para gerar ativamente uma quantidade de pontos igual à sua produção total por segundo.

Autenticação de Usuário: Um sistema completo de cadastro e login. As senhas são armazenadas de forma segura usando hashlib (com salt e hashing).

Persistência de Dados (Save/Load): O progresso do jogo (pontos, planetas, níveis) é salvo automaticamente em um arquivo JSON vinculado ao seu nome de usuário. Ao logar novamente, seu império é carregado.

Progressão de Planetas: O jogo conta com 10 planetas colonizáveis únicos (além da Terra-Mãe), cada um com seus próprios atributos de produção e imagens.

Interface Gráfica (GUI) com Pygame: Toda a interface é construída com Pygame, o que permite controle total sobre o visual.

Lista Rolável: Os planetas colonizados aparecem em uma lista vertical que pode ser navegada com o scroll do mouse.

Feedback Visual: Efeitos de texto flutuante (ex: +10) aparecem de forma sincronizada com os ganhos de pontos, tanto passivos quanto de cliques.

Arquitetura Modular: O código é limpo e separado em módulos com responsabilidades únicas.

## Estrutura do Projeto
O jogo é dividido em vários módulos para facilitar a manutenção e o entendimento:

main_pygame.py: O ponto de entrada principal. Controla a UI do Pygame, o loop principal do jogo e a máquina de estados (Login, Registro, Jogo).

modelos.py: O cérebro do jogo. Contém as classes Planeta e Imperio que gerenciam toda a lógica de jogo, produção, upgrades e a conversão dos dados para JSON (to_dict, from_dict).

gamedata.py: Um banco de dados estático que armazena os atributos de todos os planetas (nome, produção base, custo base, caminho da imagem).

visuals.py: Módulo dedicado a gerenciar os efeitos visuais, como os textos flutuantes (EfeitoFlutuante e GerenciadorDeEfeitos).

usuarios.py: Gerencia o registro e login de usuários, usando hashlib para garantir a segurança das senhas.

database.py: Um módulo utilitário simples com duas funções (salvar_json, carregar_json) que lidam com a leitura e escrita de arquivos.

## Bibliotecas Utilizadas
Este projeto depende de algumas bibliotecas, a maioria das quais já vem com o Python.

Biblioteca Principal
Pygame: A biblioteca central para toda a interface gráfica, renderização, eventos (mouse, teclado, scroll) e carregamento de imagens.

Bibliotecas Nativas do Python
json: Usado para serializar e desserializar os dados do jogo para salvamento.

hashlib: Usado no usuarios.py para criar hashes seguros (SHA256) das senhas dos usuários.

os: Usado para gerar o "salt" aleatório para as senhas e verificar a existência de arquivos.

time, math, random, sys: Módulos padrão usados para o loop do jogo, cálculos de produção e lógica geral.

## Como Executar
Para rodar este projeto em sua máquina local, siga estes passos:

Clone o repositório:


git clone [URL-DO-SEU-REPOSITÓRIO]
cd King-of-Planets
Instale o Pygame: O único requisito externo é o pygame.


pip install pygame

Execute o Jogo:


python main_pygame.py
Crie sua conta e comece a conquistar o universo!


Aqui segue uma **Captura de Tela** in-game:

<img width="494" height="787" alt="image" src="https://github.com/user-attachments/assets/d6997a41-f343-40c9-ac1f-68d1009fb344" />

