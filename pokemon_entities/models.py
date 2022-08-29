from django.db import models  # noqa F401


class Pokemon(models.Model):
    """Вид покемонов."""
    title = models.CharField('название', max_length=200)
    title_en = models.CharField('английское название', max_length=200,
                                blank=True)
    title_jp = models.CharField('японское название', max_length=200,
                                blank=True)
    description = models.TextField('описание', blank=True)
    image = models.ImageField('картинка', upload_to='pokemons',
                              null=True, blank=True)

    previous_evolution = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='next_pokemons',
        verbose_name='предыдущая эволюция',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    """Конкретный покемон."""
    lat = models.FloatField('широта')
    lon = models.FloatField('долгота')
    appeared_at = models.DateTimeField('время появления')
    disappeared_at = models.DateTimeField('время исчезновения')
    level = models.IntegerField('уровень', null=True, blank=True)
    health = models.IntegerField('здоровье', null=True, blank=True)
    strength = models.IntegerField('атака', null=True, blank=True)
    defence = models.IntegerField('защита', null=True, blank=True)
    stamina = models.IntegerField('выносливость', null=True, blank=True)

    pokemon = models.ForeignKey(
        Pokemon,
        related_name='pokemon_entities',
        verbose_name='вид покемона',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return (f'{self.pokemon.title}: {self.appeared_at} - '
                f'{self.disappeared_at}')
