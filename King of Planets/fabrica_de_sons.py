import wave
import math
import struct
import os

SAMPLE_RATE = 44100

def salvar_wav(nome_arquivo, dados_audio):
    """Escreve os dados brutos em um arquivo .wav"""
    with wave.open(nome_arquivo, 'w') as obj:
        obj.setnchannels(1) 
        obj.setsampwidth(2) 
        obj.setframerate(SAMPLE_RATE)
        
        for sample in dados_audio:
            sample = max(-1.0, min(1.0, sample))
            valor_int = int(sample * 32767)
            data = struct.pack('<h', valor_int)
            obj.writeframesraw(data)
    
    print(f"Som criado: {nome_arquivo}")

def gerar_onda_senoidal(frequencia, duracao, volume=0.5):
    """Gera uma lista de samples para uma onda senoidal"""
    n_samples = int(SAMPLE_RATE * duracao)
    audio = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        val = math.sin(2 * math.pi * frequencia * t)
        
        envelope = 1.0
        if i > n_samples - 500: 
            envelope = (n_samples - i) / 500
            
        audio.append(val * volume * envelope)
    return audio

def gerar_som_clique():
    return gerar_onda_senoidal(800, 0.05, 0.3)

def gerar_som_upgrade():
    audio = []
    duracao = 0.3
    n_samples = int(SAMPLE_RATE * duracao)
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        freq_atual = 400 + (600 * (i / n_samples))
        val = math.sin(2 * math.pi * freq_atual * t)
        val = 1.0 if val > 0 else -1.0
        
        audio.append(val * 0.2)
    return audio

def gerar_som_colonizar():
    audio = []
    duracao = 0.8
    n_samples = int(SAMPLE_RATE * duracao)
    
    freqs = [440, 554, 659] 
    
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        val = 0
        for f in freqs:
            val += math.sin(2 * math.pi * f * t)
        val = val / 3
        
        envelope = 1.0 - (i / n_samples)
        
        audio.append(val * 0.3 * envelope)
    return audio

if __name__ == "__main__":
    print("Fabricando sons...")
    salvar_wav("som_clique.wav", gerar_som_clique())
    salvar_wav("som_upgrade.wav", gerar_som_upgrade())
    salvar_wav("som_colonizar.wav", gerar_som_colonizar())
    print("Concluído! Agora rode o jogo.")