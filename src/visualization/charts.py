"""
Plotly visualizations for chess opening analytics
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional


class OpeningVisualizer:
    """Create interactive visualizations for opening analysis"""
    
    @staticmethod
    def create_efficient_frontier(df: pd.DataFrame, highlight_opening: Optional[str] = None):
        """
        Create risk-return scatter plot (like efficient frontier)
        
        Args:
            df: DataFrame with volatility and expected_return columns
            highlight_opening: Optional opening to highlight
        """
        fig = go.Figure()
        
        # Add scatter plot
        for _, row in df.iterrows():
            is_highlighted = row['opening_eco'] == highlight_opening if highlight_opening else False
            
            fig.add_trace(go.Scatter(
                x=[row['volatility']],
                y=[row['expected_return']],
                mode='markers+text',
                name=row['opening_name'],
                text=[row['opening_eco']],
                textposition='top center',
                marker=dict(
                    size=15 if is_highlighted else 10,
                    color='red' if is_highlighted else 'blue',
                    line=dict(width=2 if is_highlighted else 1)
                ),
                hovertemplate=(
                    f"<b>{row['opening_name']}</b><br>"
                    f"Expected Return: {row['expected_return']:.3f}<br>"
                    f"Volatility: {row['volatility']:.3f}<br>"
                    f"Sharpe Ratio: {row['sharpe_ratio']:.3f}<br>"
                    f"Win Rate: {row['win_rate']*100:.1f}%<br>"
                    f"Games: {row['total_games']}"
                    "<extra></extra>"
                )
            ))
        
        fig.update_layout(
            title="Chess Opening Risk-Return Profile (Efficient Frontier)",
            xaxis_title="Volatility (Risk)",
            yaxis_title="Expected Return (Points)",
            showlegend=False,
            hovermode='closest',
            height=600,
            template='plotly_dark'
        )
        
        return fig
    
    @staticmethod
    def create_sharpe_ratio_bars(df: pd.DataFrame, top_n: int = 10):
        """Create bar chart of Sharpe ratios"""
        df_sorted = df.nlargest(top_n, 'sharpe_ratio')
        
        fig = go.Figure([go.Bar(
            x=df_sorted['sharpe_ratio'],
            y=df_sorted['opening_name'],
            orientation='h',
            marker=dict(
                color=df_sorted['sharpe_ratio'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            text=df_sorted['sharpe_ratio'].round(3),
            textposition='outside',
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Sharpe Ratio: %{x:.3f}<br>"
                "<extra></extra>"
            )
        )])
        
        fig.update_layout(
            title=f"Top {top_n} Openings by Risk-Adjusted Return (Sharpe Ratio)",
            xaxis_title="Sharpe Ratio",
            yaxis_title="",
            height=500,
            template='plotly_dark'
        )
        
        return fig
    
    @staticmethod
    def create_outcome_distribution(metrics: dict):
        """Create pie chart of game outcomes"""
        labels = ['Wins', 'Draws', 'Losses']
        values = [metrics['wins'], metrics['draws'], metrics['losses']]
        colors = ['#27ae60', '#e67e22', '#c0392b']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='label+percent',
            hovertemplate="<b>%{label}</b><br>%{value} games<br>%{percent}<extra></extra>"
        )])
        
        fig.update_layout(
            title=f"{metrics['opening_name']} - Outcome Distribution",
            height=400,
            template='plotly_dark'
        )
        
        return fig
    
    @staticmethod
    def create_rating_comparison(df: pd.DataFrame, opening_eco: str):
        """Compare opening performance across rating ranges"""
        opening_data = df[df['opening_eco'] == opening_eco]
        
        fig = go.Figure()
        
        # Win rate by rating
        fig.add_trace(go.Bar(
            name='Win Rate',
            x=opening_data['rating_bin'],
            y=opening_data['win_rate'] * 100,
            marker_color='green'
        ))
        
        # Draw rate by rating
        fig.add_trace(go.Bar(
            name='Draw Rate',
            x=opening_data['rating_bin'],
            y=opening_data['draw_rate'] * 100,
            marker_color='orange'
        ))
        
        # Loss rate by rating
        fig.add_trace(go.Bar(
            name='Loss Rate',
            x=opening_data['rating_bin'],
            y=opening_data['loss_rate'] * 100,
            marker_color='red'
        ))
        
        fig.update_layout(
            title=f"Performance by Rating Range - {opening_data.iloc[0]['opening_name']}",
            xaxis_title="Rating Range",
            yaxis_title="Percentage (%)",
            barmode='stack',
            height=500,
            template='plotly_dark'
        )
        
        return fig


if __name__ == "__main__":
    # Test visualization
    sample_df = pd.DataFrame({
        'opening_eco': ['B20', 'C50'],
        'opening_name': ['Sicilian Defense', 'Italian Game'],
        'volatility': [0.4, 0.3],
        'expected_return': [0.55, 0.52],
        'sharpe_ratio': [0.15, 0.10],
        'win_rate': [0.45, 0.42],
        'total_games': [100, 100]
    })
    
    viz = OpeningVisualizer()
    fig = viz.create_efficient_frontier(sample_df)
    fig.show()
