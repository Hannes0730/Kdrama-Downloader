import re
import time
from threading import Thread

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QLineEdit, QPushButton, QListWidget, QLabel, QMessageBox, \
    QProgressBar
from PyQt5 import uic
import sys
import asyncio
from download_movie import MovieDownloader
from fetch_movie import MovieDetails, MovieFetcherThread
import json
import os
import requests


class MainUI(QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()
        self.movie_fetcher_thread = None
        self.image_url = None
        self.selected_movie_title = None
        self.selected_episode_id = None
        self.selected_episode = None
        self.movies_episodes = []
        self.selected_movie_id = None
        self.selected_movie = None
        self.movie_downloader = None
        self.movie_fetcher = None
        self.movies = None
        self.query = None
        uic.loadUi("kdrama.ui", self)
        self.setWindowIcon(QIcon("logo.png"))
        self.show()

        self.query_input = self.findChild(QLineEdit, "query_input")
        self.search_btn = self.findChild(QPushButton, "search_btn")
        self.download_btn = self.findChild(QPushButton, "download_btn")
        self.movie_list_widget = self.findChild(QListWidget, "movie_list")
        self.episode_list_widget = self.findChild(QListWidget, "episode_list")
        self.movie_image = self.findChild(QLabel, "movie_image")
        self.progress_bar = self.findChild(QProgressBar, "progress_bar")
        self.download_label = self.findChild(QLabel, "download_label")

        self.search_btn.clicked.connect(self.start_movie_fetcher_thread)
        self.query_input.returnPressed.connect(self.start_movie_fetcher_thread)
        self.download_btn.clicked.connect(self.download_selected_episode)
        self.movie_list_widget.itemSelectionChanged.connect(self.get_movie_index)
        self.episode_list_widget.itemSelectionChanged.connect(self.get_selected_episode)


    def start_movie_fetcher_thread(self):
        self.query = self.query_input.text()
        if self.query:
            self.query_input.setReadOnly(True)
            self.search_btn.setEnabled(False)
            self.movie_fetcher_thread = MovieFetcherThread(self.query)
            self.movie_fetcher_thread.movie_object_signal.connect(self.display_movies)
            self.movie_fetcher_thread.start()
        else:
            self.show_popup_error("Search Error", "Search query is empty")


    def display_movies(self, movies):
        self.movies = movies
        self.clear_movie_list()
        if self.movies:
            for movie in self.movies:
                self.movie_list_widget.addItem(movie['title'])
        self.search_btn.setEnabled(True)
        self.query_input.setReadOnly(False)

    def clear_movie_list(self):
        self.movie_list_widget.clear()



    def get_movie_index(self):
        currentRow = self.movie_list_widget.currentRow()
        if currentRow is not None:
            self.selected_movie = self.movies[currentRow]
            self.selected_movie_id = self.selected_movie['id']
            title = self.selected_movie['title']
            self.image_url = self.selected_movie['image']
            self.display_episodes()
            self.set_image()
            self.clean_title(title)
        else:
            self.show_popup_error("Search result", "No Search Result")


    def set_image(self):
        if self.image_url:
            response = requests.get(self.image_url)
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.movie_image.setScaledContents(True)
            self.movie_image.setPixmap(pixmap)
        else:
            self.movie_image.clear()


    def display_episodes(self):
        self.movie_fetcher = MovieDetails()
        self.episode_list_widget.clear()
        self.selected_episode_id = None
        self.movies_episodes = self.movie_fetcher.fetch_selected_object_detail(self.selected_movie_id)
        for episode in self.movies_episodes:
            self.episode_list_widget.addItem(episode['id'])

    def get_selected_episode(self):
        selected_item = self.episode_list_widget.currentItem()
        if selected_item is not None:
            selected_index = self.episode_list_widget.row(selected_item)
            self.selected_episode = self.movies_episodes[selected_index]
            self.selected_episode_id = self.selected_episode['id']


    def download_selected_episode(self):
        if self.selected_episode_id is not None:
            self.download_btn.setEnabled(False)
            self.download_label.setText(f'Downloading {self.selected_episode_id}')
            if not os.path.exists(os.path.join('movies', self.selected_movie_title)):
                os.mkdir(os.path.join('movies', self.selected_movie_title))
            try:
                output_path = os.path.join('movies', self.selected_movie_title, f'{self.selected_episode_id}.mp4')
                url = self.movie_fetcher.fetch_movie_streaming_links(self.selected_episode_id, self.selected_movie_id)
                self.movie_downloader = MovieDownloader(url, output_path)
                self.movie_downloader.update_progress.connect(self.update_progress)
                self.movie_downloader.download_finished.connect(self.download_finished)
                self.movie_downloader.start()
            except FileNotFoundError:
                self.show_popup_error("Missing Movie Folder", "Please create a folder named movies in the same directory of the kdrama_downloader.exe.", "Please use lowercase in creating a folder.")

        else:
            self.show_popup_error("No Episode Selected", "Please click the episode you want to download")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self):
        self.show_popup_success("Finished Download", f'{self.selected_episode_id} is finished downloading.')
        self.download_btn.setEnabled(True)
        self.download_label.setText("")
        self.progress_bar.setValue(0)

    def clean_title(self, title):
        title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        self.selected_movie_title = title.replace(' ', '-')


    def show_popup_error(self, title, content, detailedContent=""):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setDetailedText(detailedContent)
        x = msg.exec_()

    def show_popup_success(self, title, content, detailedContent=""):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(content)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setDetailedText(detailedContent)
        x = msg.exec_()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    expense_ui = MainUI()
    sys.exit(app.exec_())

