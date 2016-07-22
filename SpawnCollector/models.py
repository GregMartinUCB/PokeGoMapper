from __future__ import unicode_literals

from django.db import models

class PokeSpawns(models.Model):
    time = models.DateTimeField('Time Seen')
    pokeid = models.IntegerField()
    pokeName = models.CharField(max_length = 50, default = "")
    long = models.FloatField()
    lat = models.FloatField()
    despawn_time =models.FloatField()


