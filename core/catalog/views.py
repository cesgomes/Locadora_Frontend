from django.shortcuts import render

catalog = [
    {
        'Title':'The Dark Knight',
        'Poster': '1.jpg',
        'Available': True,
        'Watched' : False
    },
    {
        'Title': 'Inception',
        'Poster': '2.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'Fight Club',
        'Poster': '3.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'Interstellar',
        'Poster': '4.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'The Matrix',
        'Poster': '5.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'The Lord of the Rings: The Fellowship of the Ring',
        'Poster': '6.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'The Lord of the Rings: The Return of the King',
        'Poster': '7.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'The Dark Knight Rises',
        'Poster': '8.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'Se7en',
        'Poster': '9.jpg',
        'Available': True,
        'Watched': False
    },
    {
        'Title': 'The Lord of the Rings: The Two Towers',
        'Poster': '10.jpg',
        'Available': True,
        'Watched': False
    },

]

def home(request):
    return render(request, 'home.html', {'movies':catalog})
