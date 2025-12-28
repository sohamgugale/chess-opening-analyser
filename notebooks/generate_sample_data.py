"""
Generate sample chess data for testing
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from analysis.roi_calculator import OpeningROICalculator


def generate_sample_data():
    """Generate realistic sample chess data"""
    
    print("Generating sample chess data...")
    
    # Popular openings with realistic win rates AND opening moves
    openings = {
        'B20': {
            'name': 'Sicilian Defense',
            'moves': '1. e4 c5',
            'description': 'Aggressive counter-attack, fighting for center control',
            'white_win': 0.45,
            'draw': 0.25
        },
        'C50': {
            'name': 'Italian Game',
            'moves': '1. e4 e5 2. Nf3 Nc6 3. Bc4',
            'description': 'Classical opening targeting weak f7 square',
            'white_win': 0.48,
            'draw': 0.27
        },
        'D00': {
            'name': "Queen's Pawn Game",
            'moves': '1. d4 d5',
            'description': 'Solid positional play, battle for central control',
            'white_win': 0.46,
            'draw': 0.28
        },
        'E60': {
            'name': "King's Indian Defense",
            'moves': '1. d4 Nf6 2. c4 g6',
            'description': 'Dynamic counterplay with kingside attack potential',
            'white_win': 0.44,
            'draw': 0.26
        },
        'C00': {
            'name': 'French Defense',
            'moves': '1. e4 e6',
            'description': 'Solid but passive, aims for counterplay',
            'white_win': 0.43,
            'draw': 0.30
        },
        'B10': {
            'name': 'Caro-Kann Defense',
            'moves': '1. e4 c6',
            'description': 'Reliable and solid, good for positional players',
            'white_win': 0.44,
            'draw': 0.29
        },
        'A40': {
            'name': "Queen's Pawn Opening",
            'moves': '1. d4',
            'description': 'Flexible start allowing various pawn structures',
            'white_win': 0.47,
            'draw': 0.26
        },
        'C40': {
            'name': "King's Knight Opening",
            'moves': '1. e4 e5 2. Nf3',
            'description': 'Developing naturally, maintaining flexibility',
            'white_win': 0.48,
            'draw': 0.25
        },
    }
    
    # Rating ranges with adjusted probabilities
    rating_ranges = [
        (1200, 1400, 0.45, 0.25),
        (1400, 1600, 0.46, 0.26),
        (1600, 1800, 0.46, 0.27),
        (1800, 2000, 0.45, 0.28),
        (2000, 2200, 0.44, 0.30),
        (2200, 2400, 0.43, 0.32),
        (2400, 2600, 0.42, 0.35),
    ]
    
    # Generate games
    games = []
    game_id = 1
    
    for opening_eco, opening_data in openings.items():
        for rating_min, rating_max, white_adj, draw_adj in rating_ranges:
            # Fewer games at higher ratings
            if rating_min >= 2200:
                num_games = np.random.randint(50, 100)
            else:
                num_games = np.random.randint(100, 200)
            
            # Adjust probabilities by rating
            white_win = opening_data['white_win'] * white_adj / 0.45
            draw_rate = opening_data['draw'] * draw_adj / 0.25
            
            for _ in range(num_games):
                white_rating = np.random.randint(rating_min, rating_max)
                black_rating = np.random.randint(rating_min, rating_max)
                
                rand = np.random.random()
                if rand < white_win:
                    result = 'white'
                elif rand < white_win + draw_rate:
                    result = 'draw'
                else:
                    result = 'black'
                
                games.append({
                    'game_id': f'sample_{game_id}',
                    'opening_eco': opening_eco,
                    'opening_name': opening_data['name'],
                    'opening_moves': opening_data['moves'],
                    'opening_description': opening_data['description'],
                    'white_rating': white_rating,
                    'black_rating': black_rating,
                    'result': result,
                    'time_control': 'rapid',
                    'created_at': '2024-01-01'
                })
                
                game_id += 1
    
    df = pd.DataFrame(games)
    
    # Save to CSV
    output_path = Path(__file__).parent.parent / 'data' / 'processed' / 'sample_games.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Generated {len(df)} sample games")
    print(f"✓ Saved to: {output_path}")
    
    # Print summary
    print("\n📊 Summary by Rating Range:")
    df['avg_rating'] = (df['white_rating'] + df['black_rating']) / 2
    df['rating_bin'] = pd.cut(
        df['avg_rating'],
        bins=[0, 1400, 1600, 1800, 2000, 2200, 2400, 3000],
        labels=['<1400', '1400-1600', '1600-1800', '1800-2000', '2000-2200', '2200-2400', '2400+']
    )
    
    for rating_bin in df['rating_bin'].value_counts().sort_index().items():
        print(f"  • {rating_bin[0]}: {rating_bin[1]} games")
    
    print(f"\n  • Total games: {len(df)}")
    
    return df


if __name__ == "__main__":
    generate_sample_data()
