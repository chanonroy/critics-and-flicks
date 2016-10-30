from django.db import models


class Genre(models.Model):
    """ Genres for movies """
    genre = models.CharField(max_length=50)

    def __str__(self):
        return self.genre


class Actor(models.Model):
    """ Actor within a movie """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=75)
    image = models.CharField(max_length=200)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class Movie(models.Model):
    """ Movies and their details """
    title = models.CharField(max_length=80)
    director = models.CharField(max_length=100)
    year = models.CharField(max_length=5)
    description = models.TextField()
    poster = models.CharField(max_length=200)
    actors = models.ManyToManyField(Actor)
    genres = models.ManyToManyField(Genre)
    has_review = models.BooleanField(default=False)
    similars = models.ManyToManyField("self", symmetrical=False)

    def __str__(self):
        return self.title + ' ({})'.format(self.year)


class Review(models.Model):
    """ Reviews that are associated with a movie """
    review = models.TextField()
    reviewer = models.CharField(max_length=50)
    movie = models.ForeignKey(Movie)

    def __str__(self):
        return self.reviewer + ' - {}'.format(self.movie)
