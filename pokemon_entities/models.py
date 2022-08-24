from django.db import models  # noqa F401

class Pokemon(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='pokemons', null=True)

    def __str__(self):
        return f'{self.title}'


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    lat = models.FloatField()
    lon = models.FloatField()
    appeared_at = models.DateTimeField()
    disappeared_at = models.DateTimeField()

    def __str__(self):
        return (f'pokemon: {self.pokemon.title}, '
                f'lat: {self.lat}, lon: {self.lon}, '
                f'appeared at: {self.appeared_at}, '
                f'disappeared at: {self.disappeared_at}')
