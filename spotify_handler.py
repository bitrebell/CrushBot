import os
import logging
from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl

logger = logging.getLogger(__name__)

# Thread pool for running blocking operations
_executor = ThreadPoolExecutor(max_workers=3)


class SpotifyHandler:
    """Handle Spotify search and download operations."""
    
    def __init__(self, client_id: str, client_secret: str, download_dir: str = './downloads'):
        """
        Initialize Spotify handler.
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
            download_dir: Directory to save downloaded files
        """
        self.download_dir = download_dir
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Initialize Spotify client
        try:
            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.spotify = spotipy.Spotify(auth_manager=auth_manager)
            logger.info("Spotify client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Spotify client: {e}")
            self.spotify = None
        
        # Initialize Spotdl
        try:
            # Configure downloader settings
            downloader_settings = {
                "output": self.download_dir,
                "format": "mp3",
                "save_file": None,
            }
            
            self.spotdl = Spotdl(
                client_id=client_id,
                client_secret=client_secret,
                downloader_settings=downloader_settings
            )
            logger.info("Spotdl initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Spotdl: {e}")
            self.spotdl = None
    
    def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of track dictionaries
        """
        if not self.spotify:
            logger.error("Spotify client not initialized")
            return []
        
        try:
            results = self.spotify.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                track = {
                    'id': item['id'],
                    'name': item['name'],
                    'artist': ', '.join([artist['name'] for artist in item['artists']]),
                    'album': item['album']['name'],
                    'duration': self._format_duration(item['duration_ms']),
                    'duration_seconds': item['duration_ms'] // 1000,
                    'spotify_url': item['external_urls']['spotify'],
                    'preview_url': item.get('preview_url'),
                    'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None
                }
                tracks.append(track)
            
            logger.info(f"Found {len(tracks)} tracks for query: {query}")
            return tracks
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_track_by_id(self, track_id: str) -> Optional[Dict]:
        """
        Get track information by Spotify ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Track dictionary or None
        """
        if not self.spotify:
            logger.error("Spotify client not initialized")
            return None
        
        try:
            item = self.spotify.track(track_id)
            
            track = {
                'id': item['id'],
                'name': item['name'],
                'artist': ', '.join([artist['name'] for artist in item['artists']]),
                'album': item['album']['name'],
                'duration': self._format_duration(item['duration_ms']),
                'duration_seconds': item['duration_ms'] // 1000,
                'spotify_url': item['external_urls']['spotify'],
                'preview_url': item.get('preview_url'),
                'image_url': item['album']['images'][0]['url'] if item['album']['images'] else None
            }
            
            return track
            
        except Exception as e:
            logger.error(f"Error getting track by ID: {e}")
            return None
    
    def get_track_info(self, spotify_url: str) -> Optional[Dict]:
        """
        Get track information from Spotify URL.
        
        Args:
            spotify_url: Spotify track URL
            
        Returns:
            Track dictionary or None
        """
        try:
            # Extract track ID from URL
            if '/track/' in spotify_url:
                track_id = spotify_url.split('/track/')[-1].split('?')[0]
                return self.get_track_by_id(track_id)
            else:
                logger.error("Invalid Spotify URL")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing Spotify URL: {e}")
            return None
    
    async def download_track(self, track_id: str) -> Optional[str]:
        """
        Download a track by Spotify ID.
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Path to downloaded file or None
        """
        if not self.spotdl:
            logger.error("Spotdl not initialized")
            return None
        
        try:
            # Get track info
            track_info = self.get_track_by_id(track_id)
            if not track_info:
                logger.error("Track not found")
                return None
            
            spotify_url = track_info['spotify_url']
            logger.info(f"Downloading: {track_info['name']} - {track_info['artist']}")
            
            # Download the track using async method
            result = await self._download_async(spotify_url)
            return result
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    async def _download_async(self, spotify_url: str) -> Optional[str]:
        """
        Download track asynchronously.
        
        Args:
            spotify_url: Spotify track URL
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Search for the track
            songs = self.spotdl.search([spotify_url])
            
            if not songs:
                logger.error("No songs found to download")
                return None
            
            song = songs[0]
            logger.info(f"Found song: {song.name} by {song.artist}")
            
            # Use the downloader's pool_download method directly
            try:
                # Call pool_download which is an async method
                result = await self.spotdl.downloader.pool_download(song)
                
                logger.info(f"Download completed, result type: {type(result)}")
                
                # The result should be the song object with download path
                # Try to find the downloaded file in the output directory
                from pathlib import Path
                download_dir = Path(self.download_dir)
                
                if download_dir.exists():
                    # Look for the most recent mp3 file
                    mp3_files = list(download_dir.glob("*.mp3"))
                    
                    if mp3_files:
                        # Get the most recently modified file
                        latest_file = max(mp3_files, key=lambda p: p.stat().st_mtime)
                        file_path = str(latest_file)
                        
                        if os.path.exists(file_path):
                            logger.info(f"Downloaded to: {file_path}")
                            return file_path
                
                logger.error("Downloaded file not found in directory")
                return None
                
            except Exception as download_error:
                logger.error(f"Download execution error: {download_error}")
                import traceback
                traceback.print_exc()
                return None
                
        except Exception as e:
            logger.error(f"Download async error: {e}")
            import traceback
            traceback.print_exc()
            return None
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def _format_duration(ms: int) -> str:
        """
        Format duration from milliseconds to MM:SS.
        
        Args:
            ms: Duration in milliseconds
            
        Returns:
            Formatted duration string
        """
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
