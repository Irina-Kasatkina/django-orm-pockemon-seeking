import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
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
    pokemon_entities = PokemonEntity.objects.filter(appeared_at__lte=now,
                                                    disappeared_at__gte=now)

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in pokemon_entities:
        if pokemon_entity.pokemon.image:
            img_url = request.build_absolute_uri(
                          pokemon_entity.pokemon.image.url
        )
        else:
            img_url = None

        add_pokemon(
                folium_map, pokemon_entity.lat,
                pokemon_entity.lon,
                img_url
        )            

    pokemons = Pokemon.objects.all()
    pokemons_on_page = []
    for pokemon in pokemons:
        if pokemon.image:
            img_url = request.build_absolute_uri(pokemon.image.url)
        else:
            img_url = None

        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        now = localtime()
        requested_pokemon_entities = PokemonEntity.objects.filter(
                                         pokemon__id=pokemon_id,
                                         appeared_at__lte=now,
                                         disappeared_at__gte=now
        )
    except:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in requested_pokemon_entities:
        if pokemon_entity.pokemon.image:
            img_url = request.build_absolute_uri(
                          pokemon_entity.pokemon.image.url
        )
        else:
            img_url = None

        add_pokemon(
            folium_map, pokemon_entity.lat,
            pokemon_entity.lon,
            img_url
        )

    pokemon = requested_pokemon_entities[0].pokemon
    if pokemon.image:
        img_url = request.build_absolute_uri(pokemon.image.url)
    else:
        img_url = None

    pokemon_on_page = {
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
            'description': pokemon.description,
            'title_en': pokemon.title_en,
            'title_jp': pokemon.title_jp,
        }

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon_on_page
    })
