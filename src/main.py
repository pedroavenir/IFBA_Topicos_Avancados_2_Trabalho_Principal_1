
import os
from google import genai
from google.genai import types
from google.genai import errors
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import time
from pathlib import Path

with open('prompts.json', 'r', encoding='utf-8') as arquivo:
    dados = json.load(arquivo)

with open('../data/other/00_lista_resolucoes.json', 'r', encoding='utf-8') as arquivo2:
    dados2 = json.load(arquivo2)

# Load environment variables from .env file
load_dotenv()

# Retrieve the key safely
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key not found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)

def tentar_gerar_conteudo(prompt,arquivo_pdf):
    # Definir o formato do JSON para retorno usando Pydantic
    class AnaliseDocumento(BaseModel):
        titulo_documento: str = Field(description="O título principal encontrado no documento.")
        extracted: str = Field(description=prompt)

    # Configurar os parâmetros (Temperatura baixa é crucial para JSON estável)
    config = types.GenerateContentConfig(
        temperature=0.1,                 # Baixo para evitar que o modelo invente dados
        top_p=0.95,                      # Considera apenas o núcleo de alta probabilidade
        top_k=40,                        # Limita o escopo de palavras candidatas
        response_mime_type="application/json", # Força a saída a ser um JSON válido
        response_schema=AnaliseDocumento, # Passa a estrutura exata que o JSON deve seguir
    )
    """
    Tenta se comunicar com a API.
    Retorna o texto do JSON se der certo, ou None se ocorrer qualquer erro.
    """
    try:
        print("Enviando requisição para o Gemini...")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                arquivo_pdf,
                "Analise minuciosamente este arquivo PDF e extraia os dados conforme o schema JSON solicitado."
            ],
            config=config
        )
        # Se deu certo, retorna apenas o texto gerado
        return response.text

    except errors.APIError as e:
        print("\n❌ Erro de comunicação com a API do Gemini:")
        if e.code == 429:
            print("Motivo: Limite de requisições excedido ou o servidor está sobrecarregado (Erro 429).")
        elif e.code in [401, 403]:
            print("Motivo: Problema de autenticação (Erro 401/403). Verifique sua API_KEY.")
        elif e.code == 503:
            print("Motivo: O serviço do Gemini está temporariamente indisponível (Erro 503).")
        else:
            print(f"Código do Erro: {e.code} | Mensagem: {e.message}")
        return None

    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado no Python: {e}")
        return None

# isso aqui existe aoenas se dar algum erro para ele recomecar em um arquivo especifico
start_at = 0
for pdf in dados2["items"]:

    if start_at > 0:
        start_at = start_at - 1
        print("skip")
        continue

    pdf_path = pdf["path"]
    pdf_full_path = f"../data/pdfs/{pdf_path}"  # Substitua pelo caminho real do seu arquivo
    print(f"Enviando o PDF {pdf_path} para o Gemini...")
    arquivo_pdf = client.files.upload(file=pdf_full_path)

    for item in dados["extraction"]:
        print(f"ID: {item['id']}, Nome: {item['nome']}\n")

        resultado_json = None

        while resultado_json is None:
            resultado_json = tentar_gerar_conteudo(item['prompt'],arquivo_pdf)

            # Se a função retornou None, significa que deu erro dentro dela
            if resultado_json is None:
                print("Tentativa falhou. Aguardando 60 segundos para tentar novamente...\n")
                time.sleep(60)

        # Se o código saiu do loop, significa que 'resultado_json' finalmente ganhou um texto
        print("\n--- Resultado JSON Recebido com Sucesso! ---")
        print(resultado_json)
        file_path = Path(f'../data/output/gemini/gemini-3.1-flash-lite/file_{pdf["id"]}_extract_{item["id"]}.json')
        file_path.write_text(resultado_json, encoding='utf-8')
