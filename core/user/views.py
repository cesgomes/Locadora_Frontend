from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import RegistrationToken  # Criar esse model
import hashlib

# Create your views here.


def registration_sent(request):
    return render(request, 'sent.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Gerar um token único
        token = hashlib.sha256(get_random_string(50).encode()).hexdigest()

        # Criar um objeto de token com validade de 24 horas (ou tempo que preferir)
        expiration = timezone.now() + timedelta(hours=4)
        print(f'Expira as {expiration}')
        RegistrationToken.objects.create(email=email, token=token, expiration=expiration)

        # Criar o link para o usuário continuar o cadastro
        link = request.build_absolute_uri(
            reverse('complete_registration', args=[token]))

        # Enviar o e-mail com o link
        send_mail(
            'Complete seu cadastro',
            f'Por favor, clique no link para continuar o seu cadastro: {link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Redirecionar para uma página de confirmação
        # Criar uma página para confirmação
        return redirect('registration_sent')

    return render(request, 'register.html')


def complete_registration(request, token):
    token_obj = get_object_or_404(RegistrationToken, token=token) # type: ignore

    # Verificar se o token ainda é válido
    if not token_obj.is_valid():
        # Exibir uma página de erro caso o token tenha expirado
        return render(request, 'token_expired.html')

    if request.method == 'POST':
        # Processar o restante do cadastro (criar usuário, senha, etc.)
        # Excluir ou invalidar o token
        token_obj.delete()
        return redirect('registration_complete')  # Página final

    return render(request, 'complete_registration.html', {'email': token_obj.email})
