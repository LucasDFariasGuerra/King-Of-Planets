import hashlib
import os
from database import carregar_json, salvar_json

ARQUIVO_USUARIOS = "usuarios.json"

def _hash_senha(senha, salt):
    """Gera um hash seguro para a senha usando o salt."""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        senha.encode('utf-8'), 
        salt, 
        100000 
    ).hex()

def registrar_usuario(username, password):
    """
    Tenta registrar um novo usuário.
    Retorna (True, "Mensagem de sucesso") ou (False, "Mensagem de erro").
    """
    if not username or not password:
        return (False, "Usuário e senha não podem estar vazios.")
        
    dados_usuarios = carregar_json(ARQUIVO_USUARIOS)
    
    if username in dados_usuarios:
        return (False, "Este nome de usuário já existe.")
        
    salt = os.urandom(16)
    
    hash_senha = _hash_senha(password, salt)
    
    dados_usuarios[username] = {
        "salt": salt.hex(), 
        "hash_senha": hash_senha
    }
    
    if salvar_json(ARQUIVO_USUARIOS, dados_usuarios):
        return (True, "Usuário registrado com sucesso!")
    else:
        return (False, "Erro ao salvar dados do usuário.")

def login_usuario(username, password):
    """
    Tenta logar um usuário.
    Retorna (True, "Mensagem de sucesso") ou (False, "Mensagem de erro").
    """
    dados_usuarios = carregar_json(ARQUIVO_USUARIOS)
    
    if username not in dados_usuarios:
        return (False, "Usuário ou senha incorretos.")
        
    dados_usuario = dados_usuarios[username]
    
    salt = bytes.fromhex(dados_usuario["salt"])
    
    hash_salvo = dados_usuario["hash_senha"]
    
    hash_tentativa = _hash_senha(password, salt)
    
    if hash_salvo == hash_tentativa:
        return (True, "Login bem-sucedido!")
    else:
        return (False, "Usuário ou senha incorretos.")