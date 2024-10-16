from django.shortcuts import render
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente
load_dotenv()


def get_categories(session,  auth):
    

    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/GenresSet'
    csrf_token = get_csrf_token(session, sap_ep, auth)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    response = session.get(sap_ep, headers=headers, auth=auth)
    if response.status_code == 200:
        cats =  response.json().get('d', {})
        cats = {item['Id']: item['Genre'] for item in cats['results']}  
        return cats
    return {}
    
def get_sap_auth():
    """
    Retorna a autenticação básica para o SAP usando variáveis de ambiente.
    """
    usuario = os.getenv('sap_user')
    senha = os.getenv('sap_pass')
    return HTTPBasicAuth(usuario, senha) # type: ignore

def get_csrf_token(session, sap_ep, auth):
    """
    Obtém o token CSRF necessário para as requisições ao SAP.
    
    :param session: Sessão de requisição HTTP.
    :param sap_ep: Endpoint base do SAP.
    :param auth: Autenticação HTTP.
    :return: Token CSRF ou None se não for possível obtê-lo.
    """
    token_response = session.get(sap_ep, headers={"X-CSRF-Token": "Fetch"}, auth=auth)
    return token_response.headers.get("X-CSRF-Token")

def fetch_data_from_sap(session, url, headers, auth):
    """
    Faz uma requisição GET para o SAP e retorna os dados JSON.
    
    :param session: Sessão de requisição HTTP.
    :param url: URL para a requisição.
    :param headers: Cabeçalhos HTTP.
    :param auth: Autenticação HTTP.
    :return: Dados JSON da resposta ou um dicionário vazio em caso de erro.
    """
    response = session.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        return response.json().get('d', {})
    return {}

def movie_detail(request, id):
    """
    View para exibir os detalhes de um filme específico.
    
    :param request: Objeto de requisição HTTP.
    :param id: ID do filme.
    :return: Renderização da página de detalhes do filme.
    """
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/'
    sap_url = f"http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/CatalogSet({id})"
    auth = get_sap_auth()
    session = requests.Session()
    csrf_token = get_csrf_token(session, sap_ep, auth)
    cats = get_categories(session=session, auth=auth)
    detail = {}
    if csrf_token:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRF-Token": csrf_token
        }
        detail = fetch_data_from_sap(session, sap_url, headers, auth)
    detail['Genre'] = [int(cat) for cat in detail['Genre'].split(',')]
    detail['Genre'] = [cats[cat_id] for cat_id in detail['Genre']]
    detail['Genre'] = ", ".join(detail['Genre'])

    return render(request, 'movie_detail.html', {'detail': detail, 'cats': cats})

def home(request):
    """
    View para exibir a página inicial com uma lista de filmes.
    
    :param request: Objeto de requisição HTTP.
    :return: Renderização da página inicial.
    """
    
    auth = get_sap_auth()
    session = requests.Session()
    sap_url = "http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/CatalogSet?$top=12&$skip=0"
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/'
    cats = get_categories(session=session, auth=auth)    
    csrf_token = get_csrf_token(session, sap_ep, auth)


    catalog = []
    if csrf_token:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-CSRF-Token": csrf_token
        }
        catalog = fetch_data_from_sap(session, sap_url, headers, auth).get('results', [])

    return render(request, 'home.html', {'movies': catalog, 'cats':cats})

def about(request):
    """
    View para exibir a página 'Sobre'.
    
    :param request: Objeto de requisição HTTP.
    :return: Renderização da página 'Sobre'.
    """
    return render(request, 'about.html', {})