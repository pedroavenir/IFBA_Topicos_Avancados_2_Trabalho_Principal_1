import os
import json
import time
from google import genai
from google.genai.errors import APIError

GEMINI_API_KEY = "SUA_CHAVE_DE_API_AQUI"

def carregar_json(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

def buscar_gabarito_por_id(dados_gabarito, id_procurado):
    try:
        id_int = int(id_procurado)
    except ValueError:
        return None

    if isinstance(dados_gabarito, dict):
        for chave, valor in dados_gabarito.items():
            if isinstance(valor, list):
                for item in valor:
                    if isinstance(item, dict) and item.get("id") == id_int:
                        return item
        if id_procurado in dados_gabarito: return dados_gabarito[id_procurado]
        if str(id_int) in dados_gabarito: return dados_gabarito[str(id_int)]
    elif isinstance(dados_gabarito, list):
        for item in dados_gabarito:
            if isinstance(item, dict) and item.get("id") == id_int:
                return item
    return None

def avaliar_toda_a_pasta():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    config_prompts = carregar_json("./data/prompt.json")
    prompt_compara = config_prompts["comparation"]
    gabarito_humano = carregar_json("./data/other/00_lista_resolucoes.json")
    
    pasta_resultados = "./data/resultados_ia/"
    resultados_finais = []

    arquivos = [f for f in os.listdir(pasta_resultados) if f.endswith('.json')]
    
    if not arquivos:
        print("⚠️ Nenhum arquivo encontrado na pasta ./data/resultados_ia/.")
        return

    print(f"Encontrados {len(arquivos)} arquivos para avaliação. Iniciando...")

    for nome_arquivo in arquivos:
        caminho_ia = os.path.join(pasta_resultados, nome_arquivo)
        resposta_ia = carregar_json(caminho_ia)
        
        nome_limpo = nome_arquivo.replace('.json', '')
        partes = nome_limpo.split('_')
        
        if len(partes) >= 2:
            id_prompt = partes[0]
            id_pdf = partes[1]
        else:
            continue

        referencia_humana = buscar_gabarito_por_id(gabarito_humano, id_pdf)
        if not referencia_humana:
            continue

        prompt_final = f"""
        {prompt_compara}
        
        Extração da IA:
        {json.dumps(resposta_ia, ensure_ascii=False)}
        
        Gabarito Humano:
        {json.dumps(referencia_humana, ensure_ascii=False)}
        """
        
        print(f"Avaliando {nome_arquivo} (Prompt: {id_prompt}, PDF: {id_pdf})...")
        
        sucesso = False
        while not sucesso:
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_final,
                    config={
                        'temperature': 0.0,
                        'top_p': 0.1,
                        'top_k': 1
                    }
                )
                
                nota = response.text.strip()
                resultados_finais.append({
                    "arquivo": nome_arquivo,
                    "id_prompt": id_prompt,
                    "id_pdf": id_pdf,
                    "acuracia_calculada": nota
                })
                print(f"✅ Processado com sucesso!")
                sucesso = True
                time.sleep(3) 
                
            except APIError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("⚠️ Cota esgotada (Erro 429). Aguardando 60 segundos...")
                    time.sleep(60)
                else:
                    print(f"❌ Erro crítico na API: {e}")
                    break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")
                break

    caminho_salvamento = "./data/other/resultado_final_acuracia.json"
    with open(caminho_salvamento, 'w', encoding='utf-8') as f:
        json.dump(resultados_finais, f, indent=4, ensure_ascii=False)
        
    print(f"\n🎉 Tudo pronto! O relatório com todas as notas foi salvo em: {caminho_salvamento}")

if __name__ == "__main__":
    avaliar_toda_a_pasta()