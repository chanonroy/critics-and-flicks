"""
Script to retrieve movie information for the database
Run using 'python manage.py shell' and 'from movies.utils import *'
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from .models import Genre, Actor, Movie, Review
from secrets import *

taste_kid_api = taste_kid_api   # from secrets.py

def getMovie():
    """ Creates a Scrape object using the inputed movie name """
    mov = str(input('\nWhat movie to check? (q for quit)\n>>> '))
    if mov == 'q':
        return
    m = Scrape(movie=mov)
    m.check()

def getMovieDetails(m):
    """ Create a Scrape object that needs NO review """
    add = Scrape(m, review=False)
    add.check()


class Scrape(object):

    def __init__(self, movie, review=True):
        self.movie_schema = None
        self.review_needed = review
        self.filtered_reviews = []
        self.critics = []
        self.similar_list = []
        self.movie = movie
        self.movie_exists = False
        self.filters = []

    def check(self):
        """ Checks if Movie already exists in Django database """

        # Check for movie in Django DB
        if Movie.objects.filter(title=self.movie):
            print("\nMovie already exists")
            self.movie_exists = True

            # CASE 1: Movie inside Django DB, has no reviews, and needs reviews
            if Movie.objects.filter(title=self.movie, has_review=False) and self.review_needed == True:
                answer = str(input("\nWould you like to make {} a review object? (Y/N)\n>>> ".format(self.movie)))
                if answer == 'y':
                    Movie.objects.filter(title=self.movie).update(has_review=True)
                    self.get_reviews(self.movie)
                else:
                    print("\nReview not wanted. {} already exists".format(self.movie))
                    getMovie()

            # CASE 2: Movie inside Django DB, has no reviews, and does NOT need reviews
            elif Movie.objects.filter(title=self.movie, has_review=False) and self.review_needed == False:
                return

            # CASE 3: Movie inside Django DB, has reviews.
            print("Movie has reviews already. Process Ended")
            return

        # Continue on regular scraping
        self.add_movie()

    def add_movie(self):
        """ Open Movie Database API to return specific information for filtering """

        # Format OMDB API url endpoint
        omdb_name = self.movie.replace(" ", "+").lower()
        raw = requests.get("http://www.omdbapi.com/?t={}&r=json".format(omdb_name))
        movie = raw.json()

        if movie['Response'] == "False":
            print("\nMovie not found in API ...")
            if self.review_needed == False:
                return
            return

        director = movie['Director'].split(",")[0]      # Director's Full Name
        actor = movie['Actors'].split(",")[0]           # Main Actor's Full Name
        year_filmed = movie['Year']                     # Year of film release
        poster_url = movie['Poster']                    # URL for image of poster
        genres = movie['Genre']                         # Genres separated in a list
        plot = movie['Plot']                            # Movie plot

        # Split filter categories and append into one list for filtering
        self.filters.append(self.movie)
        for x in director, actor, year_filmed:
            [self.filters.append(x) for x in x.split()]

        # Confirmation Message
        print("\nTitle: {}\nDirector: {}\nYear: {}\nPlot: {} \nReviews: {}".format(self.movie, director, year_filmed, plot, self.review_needed))
        confirm = input(str("\nShall I continue, sir? (Y/N)\n>>> ")).lower()

        if confirm == 'y':
            # set self.movies_schema to this
            self.movie_schema = Movie(
                title=self.movie,
                director=director,
                year=year_filmed,
                description=plot,
                poster=poster_url,
                genre=genres,
                has_review=self.review_needed
                )
            print('Holding movie schema for {} ...\n'.format(self.movie))
        else:
            print("\nMovie details not okay. Process terminated")
            return

        if self.review_needed == False:
            self.movie_schema.save()
            return

        self.get_reviews(movie=self.movie)

    def get_reviews(self, movie):
        """ Get similar reviews from rotten tomatoes"""

        # Format rotten tomatoes url endpoint
        rt_name = movie.lower().replace(" ", "_")

        # ENHANCEMENT: allow manual entry of Rotten Tomatoes URL
        # ------------------------------------------------

        # use requests to scrape html information on movie page
        raw = requests.get("http://www.rottentomatoes.com/m/{}/reviews/?type=top_critics".format(rt_name))

        if raw is not None:
            # PARSING request HTML from Rotten Tomatoes
            soup = BeautifulSoup(raw.content, 'html.parser')
            rev = soup.find_all("div", {"class": "the_review"})
            crit = soup.find_all("a", {"class": "unstyled bold articleLink"})

            # SLICING text from beautiful soup object if it has something in it
            reviews = [x.text for x in rev[:10] if len(x.text) >= 5][:5]
            self.critics = [x.text for x in crit[:5]]

            # FILTERING for giveaway words
            self.filtered_reviews = []
            regex_filter = re.compile('|'.join(map(re.escape, self.filters)))
            for x in reviews:
                item = regex_filter.sub("---", x)
                self.filtered_reviews.append(item)

            # PRINTING for Confirmation
            for i in range(len(self.critics)):
                print(self.critics[i])
                print(self.filtered_reviews[i])
                print('\n')

            answer = str(input("Are these reviews okay? (Y/N)\n>>> ")).lower()
            if answer == 'y':
                # Check if movie needs to be saved
                if self.movie_exists == False:
                    self.movie_schema.save()
                self.get_similar()
            else:
                print("\nReviews not okay. Process terminated")
                return
        else:
            print('404 Error.')
            return

    def get_similar(self):
        """ Get list of similar movies """

        omdb_name = self.movie.replace(" ", "+").lower()
        raw = requests.get("http://www.tastekid.com/api/similar?q={}&k={}&type=movies&info=1&limit=5".format(omdb_name, taste_kid_api))
        if raw is not None:
            data = json.loads(raw.text)
            dict_parse = data['Similar']['Results']
            self.similar_list = [li['Name'] for li in dict_parse]

            # Ask if similar movie are okay
            print(self.similar_list)
            answer = str(input('\nAre these movies similar? (Y/N)\n>>> ')).lower()
            if answer == 'n':
                print('Similar objects not okay. Process ended.')
                return

            # ENHANCEMENT: allow custom entry for similar list
            # ------------------------------------------------

            # Add movie details from list of movies
            for x in self.similar_list:
                getMovieDetails(x)
                # what if one of them breaks - exception handling (tell user)

            self.save()

        else:
            print('404 Error.')

    def save(self):
        """ Saves review and similar objects into Django DB """

        answer = str(input('\nReady to save the objects? (Y/N)\n>>> ')).lower()
        if answer == 'n':
            print('Review and Similar not okay. Process ended.')
            return

        # Save Review Objects
        mov = Movie.objects.get(title=self.movie)
        for i in range(0, 5):
            rev = mov.review_set.create(review=self.filtered_reviews[i], reviewer=self.critics[i])

        print('{} is SAVED'.format(self.movie))
        return

getMovie()
