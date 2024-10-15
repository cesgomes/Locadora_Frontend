from django.shortcuts import render
import requests 
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

def home(request):
    
    load_dotenv()
    # Configurações do endpoint SAP
    sap_url = "http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/CatalogSet?$top=12&$skip=0"
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/'
    usuario = os.getenv('sap_user')
    senha = os.getenv('sap_pass')
    
    # Autenticação
    auth = HTTPBasicAuth(usuario, senha) # type: ignore

    # Pegar o token CSRF e cookies de sessão
    session = requests.Session()  # Usar session para persistir cookies
    token_response = session.get(
        sap_ep, headers={"X-CSRF-Token": "Fetch"}, auth=auth)

    csrf_token = token_response.headers.get("X-CSRF-Token")
    catalog = []  # Caso de erro, passar um array vazio

    # Certifique-se de que o token foi capturado
    if csrf_token:
        headers = {
            "Content-Type": "application/json",  # Usar JSON
            "Accept": "application/json",
            "X-CSRF-Token": csrf_token
        }
        
        # Fazer a requisição para o CatalogSet
        response = session.get(sap_url, headers=headers, auth=auth)

        # Checar se a resposta foi bem-sucedida
        if response.status_code == 200:
            # Parsear os dados JSON retornados
            catalog = response.json().get('d', {}).get('results', [])
        
    
    return render(request, 'home.html', {'movies':catalog})

def about(request):
    return render(request, 'about.html',{})
