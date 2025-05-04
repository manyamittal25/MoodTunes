from .user_dao import UserDAO
from .mood_history_dao import MoodHistoryDAO
from .listening_history_dao import ListeningHistoryDAO
from .song_dao import SongDAO
from .playlist_dao import PlaylistDAO

# Initialize all DAOs to create their tables
user_dao = UserDAO()
mood_history_dao = MoodHistoryDAO()
listening_history_dao = ListeningHistoryDAO()
song_dao = SongDAO()
playlist_dao = PlaylistDAO() 