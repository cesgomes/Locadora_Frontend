from django.shortcuts import render

# Create your views here.


def register(request):
    """
    View to display the 'About' page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered about page.
    """
    return render(request, 'register.html')
