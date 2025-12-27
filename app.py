"""
Chess Opening ROI Analyzer - Streamlit Dashboard
Applying financial analytics to chess opening selection
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from utils.data_fetcher import LichessDataFetcher, POPULAR_OPENINGS
from analysis.roi_calculator import OpeningROICalculator
from visualization.charts import OpeningVisualizer

# Page config
st.set_page_config(
    page_title="Chess Opening ROI Analyzer",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df_games' not in st.session_state:
    st.session_state.df_games = None
if 'df_metrics' not in st.session_state:
    st.session_state.df_metrics = None


def load_sample_data():
    """Load pre-computed sample data"""
    try:
        df_games = pd.read_csv('data/processed/sample_games.csv')
        st.session_state.df_games = df_games
        
        calculator = OpeningROICalculator(df_games)
        df_metrics = calculator.calculate_by_rating_ranges()
        st.session_state.df_metrics = df_metrics
        st.session_state.data_loaded = True
        return True
    except FileNotFoundError:
        return False


def main():
    # Header
    st.markdown('<h1 class="main-header">♟️ Chess Opening ROI Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Apply Financial Analytics to Chess Strategy</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.markdown("""
        <div class="info-box">
        <b>🎯 What This Tool Does:</b><br>
        Analyzes chess openings using financial metrics like:
        <ul>
            <li><b>Sharpe Ratio:</b> Risk-adjusted returns</li>
            <li><b>ROI:</b> Return on investment</li>
            <li><b>Volatility:</b> Outcome consistency</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # User rating input
        user_rating = st.slider(
            "Your Chess Rating",
            min_value=800,
            max_value=2800,
            value=1500,
            step=50,
            help="Your current chess rating (Lichess/Chess.com)"
        )
        
        # Optimization objective
        optimization_metric = st.selectbox(
            "Optimization Goal",
            options=['sharpe_ratio', 'roi', 'win_rate'],
            format_func=lambda x: {
                'sharpe_ratio': '📊 Risk-Adjusted Return (Sharpe)',
                'roi': '💰 Maximum ROI',
                'win_rate': '🏆 Highest Win Rate'
            }[x]
        )
        
        st.markdown("---")
        
        # Data loading
        st.subheader("📊 Data Source")
        
        if st.button("📥 Load Sample Data", use_container_width=True):
            with st.spinner("Loading sample data..."):
                if load_sample_data():
                    st.success("✓ Sample data loaded!")
                else:
                    st.error("Sample data not found. Please fetch new data.")
        
        st.caption("Sample data: ~1000 games from Lichess")
    
    # Main content
    if not st.session_state.data_loaded:
        st.info("👈 Click 'Load Sample Data' in the sidebar to begin analysis")
        
        # Educational content
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📈 Expected Return
            Average points scored with this opening:
            - **1.0** = Win
            - **0.5** = Draw  
            - **0.0** = Loss
            """)
        
        with col2:
            st.markdown("""
            ### 📊 Sharpe Ratio
            Risk-adjusted performance metric:
            - **> 0.5** = Excellent
            - **0.2-0.5** = Good
            - **< 0.2** = Below average
            """)
        
        with col3:
            st.markdown("""
            ### 💰 ROI
            Return on investment:
            - **Positive** = Net gains
            - **Negative** = Net losses
            - Considers volatility
            """)
        
        return
    
    # Analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Opening Recommendations",
        "📊 Risk-Return Analysis",
        "🔍 Opening Deep Dive",
        "📈 Rating Trends"
    ])
    
    # Tab 1: Recommendations
    with tab1:
        st.header("🎯 Optimal Opening for Your Rating")
        
        calculator = OpeningROICalculator(st.session_state.df_games)
        optimal_opening = calculator.get_optimal_opening(user_rating, optimization_metric)
        
        if optimal_opening:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader(f"Recommended: {optimal_opening['opening_name']}")
                st.caption(f"ECO Code: {optimal_opening['opening_eco']} | Rating Range: {optimal_opening['rating_bin']}")
                
                # Key metrics
                metric_cols = st.columns(4)
                metric_cols[0].metric("Expected Return", f"{optimal_opening['expected_return']:.3f}")
                metric_cols[1].metric("Win Rate", f"{optimal_opening['win_rate']*100:.1f}%")
                metric_cols[2].metric("Sharpe Ratio", f"{optimal_opening['sharpe_ratio']:.3f}")
                metric_cols[3].metric("ROI", f"{optimal_opening['roi']:.1f}%")
                
                # Outcome distribution
                viz = OpeningVisualizer()
                fig_outcomes = viz.create_outcome_distribution(optimal_opening)
                st.plotly_chart(fig_outcomes, use_container_width=True)
            
            with col2:
                st.markdown("""
                <div class="info-box">
                <b>📊 Analysis Insights:</b><br><br>
                <b>Sample Size:</b> {} games<br><br>
                <b>Volatility:</b> {:.3f}<br>
                <small>(Lower = More consistent)</small><br><br>
                <b>Information Ratio:</b> {:.3f}<br>
                <small>(Excess return per unit risk)</small>
                </div>
                """.format(
                    optimal_opening['total_games'],
                    optimal_opening['volatility'],
                    optimal_opening['information_ratio']
                ), unsafe_allow_html=True)
                
                st.markdown("---")
                
                st.markdown("""
                <div class="metric-card">
                <b>💡 Why This Opening?</b><br><br>
                Based on {} games at your rating level, this opening offers the best {} 
                while maintaining acceptable risk levels.
                </div>
                """.format(
                    optimal_opening['total_games'],
                    {'sharpe_ratio': 'risk-adjusted returns', 'roi': 'ROI', 'win_rate': 'win rate'}[optimization_metric]
                ), unsafe_allow_html=True)
        else:
            st.warning("Insufficient data for your rating range")
    
    # Tab 2: Risk-Return
    with tab2:
        st.header("📊 Opening Risk-Return Profiles")
        
        # Filter by rating
        rating_filter = st.selectbox(
            "Rating Range",
            options=st.session_state.df_metrics['rating_bin'].unique(),
            index=0
        )
        
        df_filtered = st.session_state.df_metrics[
            st.session_state.df_metrics['rating_bin'] == rating_filter
        ]
        
        # Efficient frontier
        viz = OpeningVisualizer()
        fig_frontier = viz.create_efficient_frontier(df_filtered)
        st.plotly_chart(fig_frontier, use_container_width=True)
        
        st.markdown("""
        <div class="info-box">
        <b>📖 How to Read This Chart:</b><br>
        • <b>Y-axis (Expected Return):</b> Higher = Better performance<br>
        • <b>X-axis (Volatility):</b> Lower = More consistent results<br>
        • <b>Top-left openings:</b> Best risk-adjusted returns (High return, Low volatility)<br>
        • <b>Hover</b> over points to see detailed statistics
        </div>
        """, unsafe_allow_html=True)
        
        # Sharpe ratio rankings
        st.subheader("🏆 Top Openings by Risk-Adjusted Return")
        fig_sharpe = viz.create_sharpe_ratio_bars(df_filtered, top_n=10)
        st.plotly_chart(fig_sharpe, use_container_width=True)
    
    # Tab 3: Deep Dive
    with tab3:
        st.header("🔍 Opening Deep Dive")
        
        # Select opening
        opening_options = st.session_state.df_metrics[['opening_eco', 'opening_name']].drop_duplicates()
        opening_options['display'] = opening_options['opening_eco'] + ' - ' + opening_options['opening_name']
        
        selected_opening = st.selectbox(
            "Select Opening",
            options=opening_options['opening_eco'].unique(),
            format_func=lambda x: opening_options[opening_options['opening_eco']==x]['display'].iloc[0]
        )
        
        # Get metrics for all rating ranges
        opening_data = st.session_state.df_metrics[
            st.session_state.df_metrics['opening_eco'] == selected_opening
        ].sort_values('rating_bin')
        
        if len(opening_data) > 0:
            # Summary metrics
            st.subheader(f"{opening_data.iloc[0]['opening_name']} - Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            avg_metrics = opening_data.mean()
            
            col1.metric("Avg Win Rate", f"{avg_metrics['win_rate']*100:.1f}%")
            col2.metric("Avg Sharpe Ratio", f"{avg_metrics['sharpe_ratio']:.3f}")
            col3.metric("Avg ROI", f"{avg_metrics['roi']:.1f}%")
            col4.metric("Total Games", f"{opening_data['total_games'].sum():.0f}")
            
            # Performance by rating
            viz = OpeningVisualizer()
            fig_rating = viz.create_rating_comparison(opening_data, selected_opening)
            st.plotly_chart(fig_rating, use_container_width=True)
            
            # Detailed table
            st.subheader("📋 Detailed Statistics by Rating")
            display_df = opening_data[[
                'rating_bin', 'total_games', 'win_rate', 'draw_rate', 
                'loss_rate', 'sharpe_ratio', 'roi', 'volatility'
            ]].copy()
            
            # Format percentages
            for col in ['win_rate', 'draw_rate', 'loss_rate']:
                display_df[col] = (display_df[col] * 100).round(1).astype(str) + '%'
            
            # Format decimals
            for col in ['sharpe_ratio', 'volatility']:
                display_df[col] = display_df[col].round(3)
            
            display_df['roi'] = display_df['roi'].round(1).astype(str) + '%'
            
            st.dataframe(display_df, use_container_width=True)
    
    # Tab 4: Rating Trends
    with tab4:
        st.header("📈 Performance Trends Across Rating Ranges")
        
        # Aggregate data by rating
        rating_agg = st.session_state.df_metrics.groupby('rating_bin').agg({
            'sharpe_ratio': 'mean',
            'roi': 'mean',
            'win_rate': 'mean',
            'total_games': 'sum'
        }).reset_index()
        
        # Create trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                rating_agg,
                x='rating_bin',
                y='sharpe_ratio',
                title='Average Sharpe Ratio by Rating',
                markers=True
            )
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                rating_agg,
                x='rating_bin',
                y='win_rate',
                title='Average Win Rate by Rating',
                markers=True
            )
            fig.update_traces(line_color='green')
            fig.update_layout(template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        
        # Games distribution
        fig = px.bar(
            rating_agg,
            x='rating_bin',
            y='total_games',
            title='Total Games Analyzed by Rating Range',
            color='total_games',
            color_continuous_scale='Blues'
        )
        fig.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Built with ♟️ by <a href="https://github.com/sohamgugale">Soham Gugale</a> | 
        Data from <a href="https://lichess.org">Lichess.org</a></p>
        <p><small>Applying quantitative finance to chess strategy</small></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
