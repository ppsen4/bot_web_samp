from flask import Flask, render_template, request
import json
import os
import wikipedia
import string

app = Flask(__name__)

# Configura o idioma da Wikipedia
wikipedia.set_lang("pt")

# Caminhos das memórias
DIR_MEMORIAS = "memorias"
MEMORIA_GIRIA = os.path.join(DIR_MEMORIAS, "giria.json")
MEMORIA_ACADEMICA = os.path.join(DIR_MEMORIAS, "academico.json")

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

# Carrega memórias com chaves normalizadas
memoria_giria = carregar_memoria(MEMORIA_GIRIA)
memoria_academica = carregar_memoria(MEMORIA_ACADEMICA)

def eh_giria(frase):
    girias = ["e aí", "td", "blz", "tranks", "tô", "parça", "mano", "véi", "consa", "mó", "demorô", "suave", "flw"]
    return any(g in frase for g in girias)

def pesquisar_na_wikipedia(pergunta):
    try:
        return wikipedia.summary(pergunta, sentences=3)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"A pergunta é ambígua. Exemplos: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Não encontrei nada sobre isso na Wikipédia."
    except Exception as e:
        return f"Ocorreu um erro: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    resposta = ""
    if request.method == "POST":
        entrada = limpar_texto(request.form["mensagem"])

        if entrada:
            estilo = "gíria" if eh_giria(entrada) else "acadêmica"
            memoria = memoria_giria if estilo == "gíria" else memoria_academica
            caminho = MEMORIA_GIRIA if estilo == "gíria" else MEMORIA_ACADEMICA

            # Busca exata
            if entrada in memoria:
                resposta = memoria[entrada]
            else:
                # Busca parcial (caso alguma chave esteja contida na entrada)
                for chave in memoria:
                    if chave in entrada:
                        resposta = memoria[chave]
                        break

                # Se nada foi encontrado, busca na Wikipedia
                if not resposta:
                    resposta = pesquisar_na_wikipedia(entrada)
                    memoria[entrada] = resposta
                    salvar_memoria(caminho, memoria)

    return render_template("index.html", resposta=resposta)

if __name__ == "__main__":
    app.run(debug=True)
