import folium
import json

# from django.http import HttpResponseNotFound
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


def show_all_pokemons(request):
    now = localtime()
    pokemons = Pokemon.objects.all()

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon in pokemons:
        for pokemon_entity in pokemon.pokemon_entities.filter(appeared_at__lte=now, 
                                                              disappeared_at__gte=now):
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


def show_pokemon(request, pokemon_id):
    pokemon = get_object_or_404(Pokemon, id=pokemon_id)

    now = localtime()
    requested_pokemon_entities = pokemon.pokemon_entities.filter(
                                    pokemon__id=pokemon_id,
                                    appeared_at__lte=now,
                                    disappeared_at__gte=now
    )

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon_entities:
        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            request.build_absolute_uri(pokemon_entity.pokemon.image.url) or None
        )

    previous_evolution_on_page = None
    if pokemon.previous_evolution:
        if previous_pokemons := Pokemon.objects.filter(id=pokemon.previous_evolution.id):
            previous_evolution_on_page = {
                'pokemon_id': previous_pokemons[0].id,
                'img_url': request.build_absolute_uri(previous_pokemons[0].image.url) or None,
                'title_ru': previous_pokemons[0].title,
            }

    next_evolution_on_page = None
    if next_pokemons := pokemon.next_pokemons.all():
        next_evolution_on_page = {
            'pokemon_id': next_pokemons[0].id,
            'img_url': request.build_absolute_uri(next_pokemons[0].image.url) or None,
            'title_ru': next_pokemons[0].title,
        }

    pokemon_on_page = {
        'pokemon_id': pokemon.id,
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
