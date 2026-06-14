import os
from google import genai
from google.genai import types
from google.genai import errors
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import json
import time
from pathlib import Path
import matplotlib.pyplot as plt

with open("prompts.json", "r", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

with open("../data/other/00_lista_resolucoes.json", "r", encoding="utf-8") as arquivo2:
    resolution_list = json.load(arquivo2)

# Load environment variables from .env file
load_dotenv()

# Retrieve the key safely
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("API Key not found. Please check your .env file.")

client = genai.Client(api_key=API_KEY)


def gemini_extract_data_from_file(prompt, arquivo_pdf):
    # Definir o formato do JSON para retorno usando Pydantic
    class AnaliseDocumento(BaseModel):
        titulo_documento: str = Field(
            description="O título principal encontrado no documento."
        )
        extracted: str = Field(description=prompt)

    # Configurar os parâmetros (Temperatura baixa é crucial para JSON estável)
    config = types.GenerateContentConfig(
        temperature=0.1,  # Baixo para evitar que o modelo invente dados
        top_p=0.95,  # Considera apenas o núcleo de alta probabilidade
        top_k=40,  # Limita o escopo de palavras candidatas
        response_mime_type="application/json",  # Força a saída a ser um JSON válido
        response_schema=AnaliseDocumento,  # Passa a estrutura exata que o JSON deve seguir
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
                "Analise minuciosamente este arquivo PDF e extraia os dados conforme o schema JSON solicitado.",
            ],
            config=config,
        )
        # Se deu certo, retorna apenas o texto gerado
        return response.text

    except errors.APIError as e:
        print("\n❌ Erro de comunicação com a API do Gemini:")
        if e.code == 429:
            print(
                "Motivo: Limite de requisições excedido ou o servidor está sobrecarregado (Erro 429)."
            )
        elif e.code in [401, 403]:
            print(
                "Motivo: Problema de autenticação (Erro 401/403). Verifique sua API_KEY."
            )
        elif e.code == 503:
            print(
                "Motivo: O serviço do Gemini está temporariamente indisponível (Erro 503)."
            )
        else:
            print(f"Código do Erro: {e.code} | Mensagem: {e.message}")
        return None

    except Exception as e:
        print(f"\n❌ Ocorreu um erro inesperado no Python: {e}")
        return None


def gemini_compare_results(ref1, ref2, extract):
    # Definir o formato do JSON para retorno usando Pydantic
    class AnaliseDocumento(BaseModel):
        result: int = Field(
            description=f'{dados["comparation"]}  "ref1":"{ref1}", "ref2": "{ref2}", "ref3": "{extract}"'
        )

    # Configurar os parâmetros (Temperatura baixa é crucial para JSON estável)
    config = types.GenerateContentConfig(
        temperature=0.1,  # Baixo para evitar que o modelo invente dados
        top_p=0.95,  # Considera apenas o núcleo de alta probabilidade
        top_k=40,  # Limita o escopo de palavras candidatas
        response_mime_type="application/json",  # Força a saída a ser um JSON válido
        response_schema=AnaliseDocumento,  # Passa a estrutura exata que o JSON deve seguir
    )

    try:
        print("Enviando requisição para o Gemini...")
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[
                "Retorne os dados conforme o schema JSON solicitado.",
            ],
            config=config,
        )
        # Se deu certo, retorna apenas o texto gerado
        return response.text

    except errors.APIError as e:
        print("\n❌ Erro de comunicação com a API do Gemini:")
        if e.code == 429:
            print(
                "Motivo: Limite de requisições excedido ou o servidor está sobrecarregado (Erro 429)."
            )
        elif e.code in [401, 403]:
            print(
                "Motivo: Problema de autenticação (Erro 401/403). Verifique sua API_KEY."
            )
        elif e.code == 503:
            print(
                "Motivo: O serviço do Gemini está temporariamente indisponível (Erro 503)."
            )
        else:
            print(f"Código do Erro: {e.code} | Mensagem: {e.message}")
        return None


def gemini_generate_extracted_data():
    # isso aqui existe aoenas se dar algum erro para ele recomecar em um arquivo especifico
    start_at = 19
    for pdf in resolution_list["items"]:

        if start_at > 0:
            start_at = start_at - 1
            print("skip")
            continue

        pdf_path = pdf["path"]
        pdf_full_path = (
            f"../data/pdfs/{pdf_path}"  # Substitua pelo caminho real do seu arquivo
        )
        print(f"Enviando o PDF {pdf_path} para o Gemini...")
        arquivo_pdf = client.files.upload(file=pdf_full_path)

        for item in dados["extraction"]:
            print(f"ID: {item['id']}, Nome: {item['nome']}\n")

            resultado_json = None

            while resultado_json is None:
                resultado_json = gemini_extract_data_from_file(
                    item["prompt"], arquivo_pdf
                )

                # Se a função retornou None, significa que deu erro dentro dela
                if resultado_json is None:
                    print(
                        "Tentativa falhou. Aguardando 60 segundos para tentar novamente...\n"
                    )
                    time.sleep(60)

            # Se o código saiu do loop, significa que 'resultado_json' finalmente ganhou um texto
            print("\n--- Resultado JSON Recebido com Sucesso! ---")
            print(resultado_json)
            file_path = Path(
                f'../data/output/gemini/gemini-3.1-flash-lite/file_{pdf["id"]}_extract_{item["id"]}.json'
            )
            file_path.write_text(resultado_json, encoding="utf-8")

def gemini_process_extracted_data(data_path):
    json_obj_result = {"data": []}

    item_counter = 0
    start_at = 0

    for pdf in resolution_list["items"]:
        if start_at > 0:
            start_at = start_at - 1
            print("skip")
            continue

        for prompt in dados["extraction"]:
            # abre o arquivo file_id_extract_id.json
            file_id = str(int(pdf["id"]))
            with open(
                f"../data/output/{data_path}/file_{file_id}_extract_{prompt["id"]}.json",
                "r",
                encoding="utf-8",
            ) as extracted:
                extracted_data = json.load(extracted)

            print(f"json file_{file_id}_extract_{prompt["id"]}.json referente ao arquivo {pdf["path"]}")
            print(f"ID: {prompt['id']}, Nome: {prompt['nome']}\n")

            # envia pra funcao enviar pro gemini
            resultado_json = None

            while resultado_json is None:
                resultado_json = gemini_compare_results(pdf["ref1"], pdf["ref2"], extracted_data["extracted"])

                # Se a função retornou None, significa que deu erro dentro dela
                if resultado_json is None:
                    print(
                        "Tentativa falhou. Aguardando 60 segundos para tentar novamente...\n"
                    )
                    time.sleep(60)

            # Se o código saiu do loop, significa que 'resultado_json' finalmente ganhou um texto
            print("\n--- Resultado JSON Recebido com Sucesso! ---")
            print(resultado_json)

            item = {
                "id": item_counter,
                "file_id": file_id,
                "extract_id": prompt["id"],
                "score": json.loads(resultado_json)["result"]
            }
            # Append each dictionary to the 'data' list
            json_obj_result["data"].append(item)

            item_counter = item_counter + 1

            with open(f"../data/output/{data_path}/result/result.json", "w", encoding="utf-8") as json_file:
                json.dump(json_obj_result, json_file, indent=4)

            print(f"File '../data/output/{data_path}/result/result.json' successfully created!")

def calcular_media_de_acerto_prompts(result_file_path):

    low_score_ignore_list = [4,8,11,19,27,34,35,42,44,45]

    with open(result_file_path,"r",encoding="utf-8",) as extracted:
        extracted_data = json.load(extracted)

    for prompt in dados["extraction"]:
        quantity = 0
        total = 0
        result = 0

        for data in extracted_data["data"]:
            if int(data["file_id"]) in low_score_ignore_list:
                #print(f"ignorado {data["file_id"]}")
                continue
            if data["extract_id"] == prompt["id"]:
                quantity = quantity + 1
                total = total + data["score"]

        result = total / quantity

        print(f"prompt: {prompt["id"]} medium: {result}")

def mostrar_acertos_por_arquivos(result_file_path):

    x_intervals = []
    performance_model_a = []
    performance_model_b = []
    performance_model_c = []

    max_plot = 100
    stop = False

    with open(result_file_path,"r",encoding="utf-8",) as extracted:
        extracted_data = json.load(extracted)

    last_arquivo = 0
    for data in extracted_data["data"]:
        if last_arquivo != data["file_id"]:
            if stop:
                break
            print(f"file number {data["file_id"]}")
            last_arquivo = data["file_id"]
            x_intervals.append(int(data["file_id"]))
            max_plot = max_plot - 1
            if not (max_plot > 0):
                stop = True

        print(f"prompt {data["extract_id"]}: {data["score"]}%")
        if data["extract_id"] == 1:
            performance_model_a.append(int(data["score"]))
        if data["extract_id"] == 2:
            performance_model_b.append(int(data["score"]))
        if data["extract_id"] == 7:
            performance_model_c.append(int(data["score"]))

    plt.plot(
        x_intervals, 
        performance_model_a, 
        marker="o", 
        linestyle="--", 
        linewidth=2, 
        label="padrão"
    )
    plt.plot(
        x_intervals, 
        performance_model_b, 
        marker="s", # 's' stands for square marker
        linestyle="-", 
        linewidth=2, 
        label="especialista"
    )
    plt.plot(
        x_intervals, 
        performance_model_c, 
        marker="^", # '^' stands for triangle marker
        linestyle="-", # dashed line just for variety
        linewidth=2, 
        label="Tree-of-Thought Prompting"
    )
    # 4. Customize Axis, Labels, and Legend
    plt.title("Comparison of Model Performance Over the Input Files", fontsize=14, fontweight="bold")
    plt.xlabel("Interval / Step (pdf)", fontsize=12)
    plt.ylabel("Performance Score", fontsize=12)
    # FORCE the legend to show up on the graph (it reads the 'label' arguments above)
    plt.legend(loc="upper left", fontsize=11)
    # Ensure every integer step is listed on the X-axis
    plt.xticks(range(min(x_intervals), max(x_intervals) + 1))
    # Add grid lines
    plt.grid(True, linestyle="--", alpha=0.5)
    # Tight layout cleans up margins
    plt.tight_layout()
    # 5. Display the final graph
    plt.show()


# EXTRAI OS DADOS USANDO GEMINI (especificamente) precisamos de versoes dessa funcao so que para outras IAs
#gemini_generate_extracted_data()

# Avalia os dados e retorna o resultado da precisao, inserir o caminho onde estao os dados e tudo sera processado pelo gemini
#gemini_process_extracted_data("gemini/gemini-3.1-flash-lite")
#gemini_process_extracted_data("mistral/mistral-medium-3.5")

# Calcula media de acertos de cada prompt por todos os arquivos
#calcular_media_de_acerto_prompts("E:/fs/code/ifba-ads/inf022/Trabalho_Principal_1/data/output/gemini/gemini-3.1-flash-lite/result/result.json")
mostrar_acertos_por_arquivos("E:/fs/code/ifba-ads/inf022/Trabalho_Principal_1/data/output/gemini/gemini-3.1-flash-lite/result/result.json")

#calcular_media_de_acerto_prompts("E:/fs/code/ifba-ads/inf022/Trabalho_Principal_1/data/output/mistral/mistral-medium-3.5/result/result.json")
#mostrar_acertos_por_arquivos("E:/fs/code/ifba-ads/inf022/Trabalho_Principal_1/data/output/mistral/mistral-medium-3.5/result/result.json")