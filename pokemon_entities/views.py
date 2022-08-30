import folium
import json
import functools
import time

from django.db import connection, reset_queries
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import localtime

from pokemon_entities.models import Pokemon, PokemonEntity


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def query_debugger(func):
    @functools.wraps(func)
    def inner_func(*args, **kwargs):
        reset_queries()
        
        start_queries = len(connection.queries)
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func


@query_debugger
def render_mainpage(request):
    pokemons = Pokemon.objects.all()
    now = localtime()
    pokemons_entities = PokemonEntity.objects.select_related('pokemon').filter(appeared_at__lte=now,
                                                                               disappeared_at__gte=now)

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemons_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url) or None
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': request.build_absolute_uri(pokemon.image.url) or None,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


@query_debugger
def render_pokemon_page(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon.objects.select_related('previous_evolution'),
                                id=pokemon_id)
    next_evolution = pokemon.next_evolutions.first()
    now = localtime()
    pokemon_entities = PokemonEntity.objects.filter(pokemon__id=pokemon_id,
                                                    appeared_at__lte=now,
                                                    disappeared_at__gte=now).select_related('pokemon')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url) or None
        )

    previous_evolution_on_page = None
    if pokemon.previous_evolution:
        previous_evolution_on_page = {
                'pokemon_id': pokemon.previous_evolution.id,
                'img_url': request.build_absolute_uri(pokemon.previous_evolution.image.url) or None,
                'title_ru': pokemon.previous_evolution.title,
        }

    next_evolution_on_page = None
    if next_evolution:
        next_evolution_on_page = {
            'pokemon_id': next_evolution.id,
            'img_url': request.build_absolute_uri(next_evolution.image.url) or None,
            'title_ru': next_evolution.title,
        }

    pokemon_on_page = {
        'pokemon_id': pokemon_id,
        'img_url': request.build_absolute_uri(pokemon.image.url) or None,
        'title_ru': pokemon.title,
        'description': pokemon.description,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'previous_evolution': previous_evolution_on_page,
        'next_evolution': next_evolution_on_page,
    }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_on_page
    })
