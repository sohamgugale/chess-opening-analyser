"""
Calculate ROI and financial metrics for chess openings
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple


class OpeningROICalculator:
    """Calculate financial metrics for chess openings"""
    
    # Point system for outcomes
    WIN_POINTS = 1.0
    DRAW_POINTS = 0.5
    LOSS_POINTS = 0.0
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with games dataframe
        
        Args:
            df: DataFrame with columns [opening_eco, result, white_rating, black_rating]
        """
        self.df = df.copy()
        self._preprocess()
        
    def _preprocess(self):
        """Preprocess the data"""
        # Calculate average rating for each game
        self.df['avg_rating'] = (self.df['white_rating'] + self.df['black_rating']) / 2
        
        # Create rating bins
        self.df['rating_bin'] = pd.cut(
            self.df['avg_rating'],
            bins=[0, 1400, 1600, 1800, 2000, 2200, 3000],
            labels=['<1400', '1400-1600', '1600-1800', '1800-2000', '2000-2200', '2200+']
        )
        
        # Convert results to points (from white's perspective)
        self.df['points'] = self.df['result'].map({
            'white': self.WIN_POINTS,
            'draw': self.DRAW_POINTS,
            'black': self.LOSS_POINTS
        })
        
    def calculate_opening_metrics(self, opening_eco: str, rating_bin: str = None) -> Dict:
        """
        Calculate all metrics for a specific opening
        
        Args:
            opening_eco: ECO code
            rating_bin: Optional rating range to filter
            
        Returns:
            Dictionary of metrics
        """
        # Filter data
        opening_df = self.df[self.df['opening_eco'] == opening_eco]
        if rating_bin:
            opening_df = opening_df[opening_df['rating_bin'] == rating_bin]
            
        if len(opening_df) == 0:
            return None
            
        # Calculate metrics
        total_games = len(opening_df)
        wins = (opening_df['result'] == 'white').sum()
        draws = (opening_df['result'] == 'draw').sum()
        losses = (opening_df['result'] == 'black').sum()
        
        # Expected return (average points)
        expected_return = opening_df['points'].mean()
        
        # Volatility (standard deviation of returns)
        volatility = opening_df['points'].std()
        
        # Sharpe Ratio (risk-adjusted return)
        # Using draw rate as "risk-free rate" (safe outcome)
        risk_free_rate = self.DRAW_POINTS
        sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Win rate
        win_rate = wins / total_games
        
        # ROI (Return on Investment)
        # Treating a draw as 0% return, win as 100% return, loss as -100% return
        roi = ((wins * 100) + (draws * 0) + (losses * -100)) / total_games
        
        # Information Ratio (excess return per unit of risk)
        benchmark_return = 0.5  # Draw rate as benchmark
        excess_return = expected_return - benchmark_return
        information_ratio = excess_return / volatility if volatility > 0 else 0
        
        return {
            'opening_eco': opening_eco,
            'opening_name': opening_df['opening_name'].iloc[0] if 'opening_name' in opening_df.columns else opening_eco,
            'total_games': total_games,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'win_rate': win_rate,
            'draw_rate': draws / total_games,
            'loss_rate': losses / total_games,
            'expected_return': expected_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'roi': roi,
            'information_ratio': information_ratio,
            'rating_bin': rating_bin
        }
    
    def calculate_all_openings(self, rating_bin: str = None) -> pd.DataFrame:
        """Calculate metrics for all openings"""
        results = []
        
        openings = self.df['opening_eco'].unique()
        for opening in openings:
            metrics = self.calculate_opening_metrics(opening, rating_bin)
            if metrics:
                results.append(metrics)
                
        return pd.DataFrame(results).sort_values('sharpe_ratio', ascending=False)
    
    def calculate_by_rating_ranges(self) -> pd.DataFrame:
        """Calculate metrics for all openings across all rating ranges"""
        all_results = []
        
        for rating_bin in self.df['rating_bin'].unique():
            if pd.notna(rating_bin):
                results = self.calculate_all_openings(rating_bin)
                all_results.append(results)
                
        return pd.concat(all_results, ignore_index=True)
    
    def get_optimal_opening(self, user_rating: int, metric: str = 'sharpe_ratio') -> Dict:
        """
        Recommend optimal opening for a specific rating
        
        Args:
            user_rating: User's chess rating
            metric: Metric to optimize ('sharpe_ratio', 'roi', 'win_rate')
            
        Returns:
            Best opening metrics
        """
        # Determine rating bin
        if user_rating < 1400:
            rating_bin = '<1400'
        elif user_rating < 1600:
            rating_bin = '1400-1600'
        elif user_rating < 1800:
            rating_bin = '1600-1800'
        elif user_rating < 2000:
            rating_bin = '1800-2000'
        elif user_rating < 2200:
            rating_bin = '2000-2200'
        else:
            rating_bin = '2200+'
            
        # Get all openings for this rating
        openings = self.calculate_all_openings(rating_bin)
        
        # Filter for minimum sample size
        openings = openings[openings['total_games'] >= 10]
        
        if len(openings) == 0:
            return None
            
        # Get best opening by metric
        best_opening = openings.nlargest(1, metric).iloc[0]
        
        return best_opening.to_dict()


if __name__ == "__main__":
    # Test with sample data
    sample_data = pd.DataFrame({
        'opening_eco': ['B20', 'B20', 'C50', 'C50'] * 10,
        'result': ['white', 'draw', 'black', 'white'] * 10,
        'white_rating': [1500] * 40,
        'black_rating': [1500] * 40
    })
    
    calculator = OpeningROICalculator(sample_data)
    metrics = calculator.calculate_all_openings()
    print(metrics)
