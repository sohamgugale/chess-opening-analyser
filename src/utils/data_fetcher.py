"""
Data fetcher for chess games from Lichess database
"""
import requests
import pandas as pd
import chess.pgn
import io
from tqdm import tqdm
import time
from typing import List, Dict, Optional
import json


class LichessDataFetcher:
    """Fetch chess games from Lichess API"""
    
    BASE_URL = "https://lichess.org/api"
    
    def __init__(self, max_games: int = 10000):
        self.max_games = max_games
        self.session = requests.Session()
        
    def fetch_games_by_opening(
        self, 
        opening_eco: str,
        rating_min: int = 1200,
        rating_max: int = 2000,
        time_control: str = "rapid"
    ) -> List[Dict]:
        """
        Fetch games for a specific opening
        
        Args:
            opening_eco: ECO code (e.g., "B20" for Sicilian)
            rating_min: Minimum player rating
            rating_max: Maximum player rating
            time_control: Time control (rapid, blitz, bullet)
            
        Returns:
            List of game dictionaries
        """
        print(f"Fetching games for {opening_eco} ({rating_min}-{rating_max})...")
        
        params = {
            "opening": opening_eco,
            "since": "2023-01-01",  # Recent games
            "max": min(self.max_games, 5000),  # API limit per request
            "rated": "true",
            "perfType": time_control,
            "moves": "false",  # We don't need full game moves
            "clocks": "false"
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/games",
                params=params,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            games = []
            for line in response.iter_lines():
                if line:
                    game_data = json.loads(line.decode('utf-8'))
                    
                    # Filter by rating
                    white_rating = game_data.get('players', {}).get('white', {}).get('rating', 0)
                    black_rating = game_data.get('players', {}).get('black', {}).get('rating', 0)
                    
                    if rating_min <= white_rating <= rating_max and rating_min <= black_rating <= rating_max:
                        games.append(self._parse_game(game_data))
                        
                    if len(games) >= self.max_games:
                        break
                        
            print(f"  ✓ Fetched {len(games)} games")
            return games
            
        except Exception as e:
            print(f"  ✗ Error fetching {opening_eco}: {e}")
            return []
    
    def _parse_game(self, game_data: Dict) -> Dict:
        """Parse game data into structured format"""
        result = game_data.get('winner', 'draw')
        
        return {
            'game_id': game_data.get('id'),
            'white_rating': game_data.get('players', {}).get('white', {}).get('rating'),
            'black_rating': game_data.get('players', {}).get('black', {}).get('rating'),
            'result': result,  # 'white', 'black', or 'draw'
            'opening_eco': game_data.get('opening', {}).get('eco'),
            'opening_name': game_data.get('opening', {}).get('name'),
            'time_control': game_data.get('speed'),
            'created_at': game_data.get('createdAt')
        }
    
    def fetch_multiple_openings(
        self,
        opening_codes: List[str],
        rating_ranges: List[tuple] = [(1200, 1600), (1600, 2000), (2000, 2400)]
    ) -> pd.DataFrame:
        """
        Fetch games for multiple openings across rating ranges
        
        Args:
            opening_codes: List of ECO codes
            rating_ranges: List of (min, max) rating tuples
            
        Returns:
            DataFrame with all games
        """
        all_games = []
        
        total_fetches = len(opening_codes) * len(rating_ranges)
        progress_bar = tqdm(total=total_fetches, desc="Fetching data")
        
        for opening in opening_codes:
            for rating_min, rating_max in rating_ranges:
                games = self.fetch_games_by_opening(
                    opening,
                    rating_min=rating_min,
                    rating_max=rating_max
                )
                all_games.extend(games)
                progress_bar.update(1)
                time.sleep(1)  # Rate limiting
                
        progress_bar.close()
        
        df = pd.DataFrame(all_games)
        print(f"\n✓ Total games fetched: {len(df)}")
        return df


# Popular opening ECO codes
POPULAR_OPENINGS = {
    'B20': 'Sicilian Defense',
    'C50': 'Italian Game',
    'D00': "Queen's Pawn Game",
    'E60': "King's Indian Defense",
    'C00': 'French Defense',
    'B10': 'Caro-Kann Defense',
    'A40': "Queen's Pawn Opening",
    'C40': "King's Knight Opening",
    'B00': "King's Pawn Opening",
    'A00': 'Uncommon Opening'
}


if __name__ == "__main__":
    # Test the fetcher
    fetcher = LichessDataFetcher(max_games=100)
    df = fetcher.fetch_multiple_openings(
        opening_codes=list(POPULAR_OPENINGS.keys())[:3],
        rating_ranges=[(1400, 1800)]
    )
    print(df.head())
    print(f"\nShape: {df.shape}")
