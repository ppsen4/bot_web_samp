from flask import Flask, render_template, request
import json
import os
import wikipedia
import string
from difflib import get_close_matches

app = Flask(__name__)

# Configura o idioma da Wikipedia
wikipedia.set_lang("pt")

# Caminhos das memórias
DIR_MEMORIAS = "memorias"
MEMORIA_GIRIA = os.path.join(DIR_MEMORIAS, "giria.json")
MEMORIA_ACADEMICA = os.path.join(DIR_MEMORIAS, "academico.json")
MEMORIA_ERRO = os.path.join(DIR_MEMORIAS, "palavra_erro.json")

# Funções de utilidade
def limpar_texto(texto):
    return texto.translate(str.maketrans("", "", string.punctuation)).strip().lower()

def carregar_memoria(caminho):
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
            return {limpar_texto(k): v for k, v in dados.items()}
    return {}

def salvar_memoria(caminho, memoria):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=4)

# Carrega todas as memórias
memorias = {
    "giria": carregar_memoria(MEMORIA_GIRIA),
    "academico": carregar_memoria(MEMORIA_ACADEMICA),
    "erro": carregar_memoria(MEMORIA_ERRO)
}

def pesquisar_na_wikipedia(pergunta):
    try:
        return wikipedia.summary(pergunta, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"A pergunta é ambígua. Exemplos: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Não encontrei nada sobre isso na Wikipédia."
    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"

def buscar_resposta(entrada):
    entrada_limpa = limpar_texto(entrada)
    
    # Busca exata
    for categoria, memoria in memorias.items():
        if entrada_limpa in memoria:
            return memoria[entrada_limpa]
    
    # Busca aproximada (caso alguma chave seja parecida)
    for categoria, memoria in memorias.items():
        correspondencias = get_close_matches(entrada_limpa, memoria.keys(), n=1, cutoff=0.6)
        if correspondencias:
            return memoria[correspondencias[0]]

    # Se nada foi encontrado, busca na Wikipedia e salva na categoria mais apropriada
    resposta_wiki = pesquisar_na_wikipedia(entrada)
    
    estilo = "giria" if any(g in entrada_limpa for g in memorias["giria"].keys()) else "academico"
    salvar_memoria(os.path.join(DIR_MEMORIAS, f"{estilo}.json"), {entrada_limpa: resposta_wiki})
    
    return resposta_wiki

@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    if request.method == "POST":
        entrada_original = request.form["mensagem"]
        resposta = buscar_resposta(entrada_original)

    return render_template("index.html", resposta=resposta)

if __name__ == "__main__":
    app.run(debug=True)