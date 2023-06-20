import os
import json
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from dotenv import load_dotenv

load_dotenv()

SERVIDOR = os.getenv("SERVIDOR")
PASTA_ANDROID = "android"
PASTA_APPLE = "apple"
CHAVE_API = os.getenv("CHAVE_API")


def fazer_upload(caminho_arquivo):
    print("Fazendo upload do arquivo:", caminho_arquivo)
    nome_arquivo = os.path.basename(caminho_arquivo)
    multipart_data = MultipartEncoder(fields={'file': (nome_arquivo, open(caminho_arquivo, 'rb'), 'application/octet-stream')})
    headers = {'Content-Type': multipart_data.content_type, 'Authorization': CHAVE_API}
    response = requests.post(SERVIDOR + '/api/v1/upload', data=multipart_data, headers=headers)
    print(response.text)
    return response.text


def realizar_scan(data):
    print("Realizando scan do arquivo")
    post_dict = json.loads(data)
    headers = {'Authorization': CHAVE_API}
    response = requests.post(SERVIDOR + '/api/v1/scan', data=post_dict, headers=headers)
    #print(response.text)


def gerar_pdf(data, caminho_arquivo):
    print("Gerando relatório PDF")
    headers = {'Authorization': CHAVE_API}
    nome_ipa = os.path.splitext(os.path.basename(caminho_arquivo))[0]
    data = {"hash": json.loads(data)["hash"], "pdf_name": nome_ipa}
    response = requests.post(SERVIDOR + '/api/v1/download_pdf', data=data, headers=headers, stream=True)
    with open(f"{nome_ipa}.pdf", 'wb') as flip:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                flip.write(chunk)
    print(f"Relatório salvo como {nome_ipa}.pdf")


def gerar_json(data):
    print("Gerando relatório JSON")
    headers = {'Authorization': CHAVE_API}
    data = {"hash": json.loads(data)["hash"]}
    response = requests.post(SERVIDOR + '/api/v1/report_json', data=data, headers=headers)
    #print(response.text)


def deletar_scan(data):
    print("Deletando scan")
    headers = {'Authorization': CHAVE_API}
    data = {"hash": json.loads(data)["hash"]}
    response = requests.post(SERVIDOR + '/api/v1/delete_scan', data=data, headers=headers)
    #print(response.text)


# Verificar pasta "android"
if os.path.exists(PASTA_ANDROID):
    print("Verificando pasta 'android'")
    arquivos_apk = [arquivo for arquivo in os.listdir(PASTA_ANDROID) if arquivo.endswith(".apk")]
    for arquivo_apk in arquivos_apk:
        caminho_arquivo = os.path.join(PASTA_ANDROID, arquivo_apk)
        resposta = fazer_upload(caminho_arquivo)
        realizar_scan(resposta)
        gerar_json(resposta)
        gerar_pdf(resposta, caminho_arquivo)
        #deletar_scan(resposta)
else:
    print("A pasta 'android' não existe.")

# Verificar pasta "apple"
if os.path.exists(PASTA_APPLE):
    print("Verificando pasta 'apple'")
    arquivos_ipa = [arquivo for arquivo in os.listdir(PASTA_APPLE) if arquivo.endswith(".ipa")]
    for arquivo_ipa in arquivos_ipa:
        caminho_arquivo = os.path.join(PASTA_APPLE, arquivo_ipa)
        resposta = fazer_upload(caminho_arquivo)
        realizar_scan(resposta)
        gerar_json(resposta)
        gerar_pdf(resposta, caminho_arquivo)
        #deletar_scan(resposta)
else:
    print("A pasta 'apple' não existe.")
