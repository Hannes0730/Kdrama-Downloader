import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal


class MovieDetails:
    def __init__(self):
        super().__init__()
        self.has_next_page = True
        self.current_page = 1
        self.movie_list = []

    def fetch_object(self, query):
        while self.has_next_page:
            response = requests.get(f'https://api.consumet.org/movies/dramacool/{query}', params={'page': self.current_page})
            data = response.json()
            self.has_next_page = data['hasNextPage']
            if self.has_next_page:
                self.current_page += 1

            for result in data['results']:
                result_dict = {
                    'id': result['id'],
                    'title': result['title'],
                    'image': result['image']
                }
                self.movie_list.append(result_dict)

        return self.movie_list

    def fetch_selected_object_detail(self, selected_movie):
        movie_info = []
        response = requests.get(f'https://api.consumet.org/movies/dramacool/info', params={'id': {selected_movie}})
        data = response.json()

        for result in data['episodes']:
            result_dict = {
                'id': result['id'],
                'title': result['title']
            }

            movie_info.append(result_dict)

        return movie_info


    def fetch_movie_streaming_links(self, selected_episode_id, selected_media_id):
        response = requests.get('https://api.consumet.org/movies/dramacool/watch', params={"episodeId": selected_episode_id, "mediaId": selected_media_id,
                                             "server": "asianload"})
        data = response.json()
        url = data['sources'][-1]['url']
        url_full_hd = url.rsplit('.', 1)[0] + ".720." + url.rsplit('.', 1)[1]

        return url_full_hd

class MovieFetcherThread(QThread):
    movie_object_signal = pyqtSignal(list)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        movie_fetcher = MovieDetails()
        movies = movie_fetcher.fetch_object(self.query)
        self.movie_object_signal.emit(movies)