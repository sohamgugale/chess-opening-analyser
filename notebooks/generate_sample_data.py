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
    
    # Popular openings with realistic win rates
    openings = {
        'B20': {'name': 'Sicilian Defense', 'white_win': 0.45, 'draw': 0.25},
        'C50': {'name': 'Italian Game', 'white_win': 0.48, 'draw': 0.27},
        'D00': {'name': "Queen's Pawn Game", 'white_win': 0.46, 'draw': 0.28},
        'E60': {'name': "King's Indian Defense", 'white_win': 0.44, 'draw': 0.26},
        'C00': {'name': 'French Defense', 'white_win': 0.43, 'draw': 0.30},
        'B10': {'name': 'Caro-Kann Defense', 'white_win': 0.44, 'draw': 0.29},
        'A40': {'name': "Queen's Pawn Opening", 'white_win': 0.47, 'draw': 0.26},
        'C40': {'name': "King's Knight Opening", 'white_win': 0.48, 'draw': 0.25},
    }
    
    # Rating ranges
    rating_ranges = [
        (1200, 1400),
        (1400, 1600),
        (1600, 1800),
        (1800, 2000),
        (2000, 2200)
    ]
    
    # Generate games
    games = []
    game_id = 1
    
    for opening_eco, opening_data in openings.items():
        for rating_min, rating_max in rating_ranges:
            # Generate 100-200 games per opening per rating range
            num_games = np.random.randint(100, 200)
            
            for _ in range(num_games):
                # Random ratings in range
                white_rating = np.random.randint(rating_min, rating_max)
                black_rating = np.random.randint(rating_min, rating_max)
                
                # Determine result based on probabilities
                rand = np.random.random()
                if rand < opening_data['white_win']:
                    result = 'white'
                elif rand < opening_data['white_win'] + opening_data['draw']:
                    result = 'draw'
                else:
                    result = 'black'
                
                games.append({
                    'game_id': f'sample_{game_id}',
                    'opening_eco': opening_eco,
                    'opening_name': opening_data['name'],
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
    print("\n📊 Summary:")
    print(f"  • Openings: {len(openings)}")
    print(f"  • Rating ranges: {len(rating_ranges)}")
    print(f"  • Total games: {len(df)}")
    print(f"  • White wins: {(df['result'] == 'white').sum()}")
    print(f"  • Draws: {(df['result'] == 'draw').sum()}")
    print(f"  • Black wins: {(df['result'] == 'black').sum()}")
    
    # Test calculator
    print("\n🧮 Testing calculator...")
    calculator = OpeningROICalculator(df)
    metrics = calculator.calculate_all_openings()
    print("\nTop 3 openings by Sharpe Ratio:")
    print(metrics.head(3)[['opening_name', 'sharpe_ratio', 'roi', 'win_rate']])
    
    return df


if __name__ == "__main__":
    generate_sample_data()
