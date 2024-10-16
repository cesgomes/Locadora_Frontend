from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views import View
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do .env
load_dotenv()


class MyDataView(View):
    """View para demonstrar paginação simples com dados estáticos."""

    def get(self, request, *args, **kwargs):
        data = self.get_data()
        paginator = Paginator(data, 12)  # Paginando em blocos de 12 itens
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return JsonResponse({
            'items': page_obj.object_list,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
        })

    def get_data(self):
        """Retorna uma lista de dados fictícios."""
        return [{"id": i, "name": f"Item {i}"} for i in range(1, 251)]


def get_sap_auth():
    """Retorna a autenticação básica usando variáveis de ambiente."""
    return HTTPBasicAuth(os.getenv('sap_user'), os.getenv('sap_pass'))  # type: ignore


def get_csrf_token(session, sap_ep, auth):
    """Obtém o token CSRF para ser utilizado nas requisições."""
    response = session.get(
        sap_ep, headers={"X-CSRF-Token": "Fetch"}, auth=auth)
    return response.headers.get("X-CSRF-Token")


def fetch_data_from_sap(session, url, headers, auth):
    """Realiza requisições ao serviço OData do SAP e retorna dados JSON."""
    response = session.get(url, headers=headers, auth=auth)
    try:
        return response.json().get('d', {})
    except ValueError:
        print(f'Erro ao parsear JSON: {response.text}')
        return {}


def get_categories(session, auth):
    """Obtém e retorna a lista de categorias do serviço SAP."""
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/GenresSet'
    csrf_token = get_csrf_token(session, sap_ep, auth)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    response = session.get(sap_ep, headers=headers, auth=auth)
    if response.status_code == 200:
        return {item['Id']: item['Genre'] for item in response.json().get('d', {}).get('results', [])}
    return {}


def get_total_records(session, sap_ep, headers, auth):
    """Obtém o total de registros disponíveis para uma coleção do SAP."""
    response = session.get(sap_ep, headers=headers, auth=auth)
    if response.status_code == 200:
        return len(response.json().get('d', {}).get('results', []))
    return 0


def home(request):
    """View para exibir a página inicial com a lista de filmes paginada."""
    auth = get_sap_auth()
    session = requests.Session()
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/'
    cats = get_categories(session, auth)
    csrf_token = get_csrf_token(session, sap_ep, auth)

    page = int(request.GET.get('page', 1))
    items_per_page = 12
    skip = (page - 1) * items_per_page
    sap_url = f"{sap_ep}CatalogSet?$top={items_per_page}&$skip={skip}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }

    catalog = fetch_data_from_sap(
        session, sap_url, headers, auth).get('results', [])
    total_records = get_total_records(
        session, f"{sap_ep}CatalogSet?$count", headers, auth)
    total_pages = (total_records + items_per_page - 1) // items_per_page
    page_numbers = list(range(1, total_pages + 1))

    return render(request, 'home.html', {
        'movies': catalog,
        'cats': cats,
        'current_page': page,
        'total_pages': total_pages,
        'page_numbers': page_numbers
    })


def categories(request, id):
    """View para exibir filmes filtrados por categoria, com paginação."""
    auth = get_sap_auth()
    session = requests.Session()
    print(id)
    cats = get_categories(session, auth)

    page = int(request.GET.get('page', 1))
    items_per_page = 12
    skip = (page - 1) * items_per_page
    sap_ep = 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/'
    sap_url = f"{sap_ep}CatalogSet?$top={items_per_page}&$skip={
        skip}&$filter=substringof('{id}',Genre) and true"

    csrf_token = get_csrf_token(session, sap_ep, auth)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }

    catalog = fetch_data_from_sap(
        session, sap_url, headers, auth).get('results', [])
    count_url = f"{sap_ep}CatalogSet?$count&$filter=substringof('{
        id}',Genre) and true"
    total_records = get_total_records(session, count_url, headers, auth)
    total_pages = (total_records + items_per_page - 1) // items_per_page
    page_numbers = list(range(1, total_pages + 1))

    return render(request, 'categorie.html', {
        'movies': catalog,
        'cats': cats,
        'cat': cats.get(id),
        'current_page': page,
        'total_pages': total_pages,
        'page_numbers': page_numbers
    })


def movie_detail(request, id):
    """View para exibir detalhes de um filme específico."""
    auth = get_sap_auth()
    session = requests.Session()
    sap_url = f"http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/CatalogSet({
        id})"
    cats = get_categories(session, auth)
    csrf_token = get_csrf_token(
        session, 'http://localhost:8000/sap/opu/odata/SAP/Z_BLOCKBUSTER_SRV/', auth)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CSRF-Token": csrf_token
    }
    detail = fetch_data_from_sap(session, sap_url, headers, auth)
    detail['Genre'] = ", ".join([cats[int(cat)]
                                for cat in detail['Genre'].split(',')])

    return render(request, 'movie_detail.html', {'detail': detail, 'cats': cats})


def about(request):
    """View para exibir a página 'Sobre'."""
    return render(request, 'about.html')
