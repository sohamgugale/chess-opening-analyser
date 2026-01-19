"""
Chess Opening ROI Analyzer - Professional Dashboard
Applying Quantitative Finance to Chess Strategy
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import requests
from threading import Thread
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from utils.data_fetcher import LichessDataFetcher, POPULAR_OPENINGS
from analysis.roi_calculator import OpeningROICalculator
from visualization.charts import OpeningVisualizer

# Keep-alive function to prevent Streamlit from sleeping
def keep_alive():
    """Pings the app every 14 minutes to prevent Streamlit Cloud from sleeping"""
    app_url = st.secrets.get("APP_URL", "")  # Set this in Streamlit secrets
    
    if not app_url:
        return  # Don't run if URL not configured
    
    while True:
        time.sleep(14 * 60)  # Sleep for 14 minutes
        try:
            requests.get(app_url, timeout=10)
        except Exception:
            pass  # Silently fail if ping doesn't work

# Start keep-alive thread (only once)
if 'keep_alive_started' not in st.session_state:
    try:
        thread = Thread(target=keep_alive, daemon=True)
        thread.start()
        st.session_state.keep_alive_started = True
    except Exception:
        pass  # If threading fails, continue without keep-alive

# Page config
st.set_page_config(
    page_title="Chess Opening ROI Analyzer | Quantitative Strategy",
    page_icon="♔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Chess-Themed CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Cinzel:wght@400;600;700&family=Lora:wght@400;500;600&display=swap');
    
    /* Global Styles */
    :root {
        --chess-dark: #1a1410;
        --chess-board-dark: #b58863;
        --chess-board-light: #f0d9b5;
        --chess-gold: #d4af37;
        --chess-silver: #c0c0c0;
        --chess-ivory: #fffff0;
        --accent-red: #c41e3a;
        --accent-green: #228b22;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main background with chess board pattern */
    .stApp {
        background: linear-gradient(135deg, #1a1410 0%, #2d2419 100%);
        color: var(--chess-ivory);
    }
    
    /* Chess board background pattern */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            repeating-linear-gradient(
                0deg,
                transparent,
                transparent 70px,
                rgba(181, 136, 99, 0.03) 70px,
                rgba(181, 136, 99, 0.03) 140px
            ),
            repeating-linear-gradient(
                90deg,
                transparent,
                transparent 70px,
                rgba(181, 136, 99, 0.03) 70px,
                rgba(181, 136, 99, 0.03) 140px
            );
        opacity: 0.5;
        pointer-events: none;
        z-index: 0;
    }
    
    /* Main header */
    .main-header {
        font-family: 'Cinzel', serif;
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, var(--chess-gold) 0%, var(--chess-silver) 50%, var(--chess-gold) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 2rem 0 0.5rem 0;
        text-shadow: 0 0 30px rgba(212, 175, 55, 0.3);
        letter-spacing: 2px;
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    .sub-header {
        font-family: 'Lora', serif;
        text-align: center;
        color: var(--chess-board-light);
        font-size: 1.3rem;
        margin-bottom: 3rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 300;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d2419 0%, #1a1410 100%);
        border-right: 2px solid var(--chess-gold);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-family: 'Cinzel', serif;
        color: var(--chess-gold);
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(181, 136, 99, 0.15) 0%, rgba(240, 217, 181, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-left: 4px solid var(--chess-gold);
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        color: var(--chess-ivory);
    }
    
    .info-box b {
        color: var(--chess-gold);
        font-family: 'Cinzel', serif;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(192, 192, 192, 0.05) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.4);
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.2);
        transition: all 0.3s ease;
        color: var(--chess-ivory);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.4);
        border-color: var(--chess-gold);
    }
    
    .metric-card b {
        color: var(--chess-gold);
        font-family: 'Cinzel', serif;
        font-size: 1.1rem;
    }
    
    /* Strategy cards */
    .strategy-card {
        background: linear-gradient(135deg, rgba(181, 136, 99, 0.2) 0%, rgba(240, 217, 181, 0.1) 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid rgba(212, 175, 55, 0.3);
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .strategy-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent 30%, rgba(212, 175, 55, 0.1) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s;
    }
    
    .strategy-card:hover::before {
        transform: translateX(100%);
    }
    
    .strategy-card:hover {
        border-color: var(--chess-gold);
        box-shadow: 0 10px 40px rgba(212, 175, 55, 0.3);
        transform: translateY(-3px);
    }
    
    .strategy-title {
        font-family: 'Cinzel', serif;
        font-size: 1.3rem;
        color: var(--chess-gold);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .strategy-subtitle {
        font-family: 'Lora', serif;
        color: var(--chess-board-light);
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .strategy-desc {
        color: rgba(255, 255, 240, 0.8);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Buttons */
    .stButton > button {
        font-family: 'Cinzel', serif;
        background: linear-gradient(135deg, var(--chess-gold) 0%, #b8860b 100%);
        color: var(--chess-dark);
        border: none;
        border-radius: 8px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(212, 175, 55, 0.5);
        background: linear-gradient(135deg, #ffd700 0%, var(--chess-gold) 100%);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(26, 20, 16, 0.5);
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cinzel', serif;
        font-weight: 600;
        color: var(--chess-board-light);
        background: rgba(181, 136, 99, 0.2);
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--chess-gold) 0%, #b8860b 100%);
        color: var(--chess-dark);
        border-color: var(--chess-gold);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--chess-gold);
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Cinzel', serif;
        color: var(--chess-board-light);
        font-size: 0.9rem;
        letter-spacing: 1px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Cinzel', serif;
        color: var(--chess-gold);
        background: rgba(181, 136, 99, 0.15);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 8px;
    }
    
    /* Dataframe */
    .dataframe {
        font-family: 'Lora', serif;
        color: var(--chess-ivory);
    }
    
    /* Selectbox, slider */
    .stSelectbox label, .stSlider label {
        font-family: 'Cinzel', serif;
        color: var(--chess-gold);
        font-weight: 600;
    }
    
    /* Chess piece decorations */
    .chess-piece-deco {
        font-size: 3rem;
        opacity: 0.15;
        position: absolute;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    /* Opening name highlight */
    .opening-name {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: var(--chess-gold);
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: rgba(212, 175, 55, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .stat-item {
        background: rgba(181, 136, 99, 0.15);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        text-align: center;
    }
    
    .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--chess-gold);
    }
    
    .stat-label {
        font-family: 'Cinzel', serif;
        font-size: 0.85rem;
        color: var(--chess-board-light);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Footer */
    .custom-footer {
        font-family: 'Lora', serif;
        text-align: center;
        color: var(--chess-board-light);
        margin-top: 4rem;
        padding: 2rem;
        border-top: 2px solid rgba(212, 175, 55, 0.3);
    }
    
    .custom-footer a {
        color: var(--chess-gold);
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .custom-footer a:hover {
        color: #ffd700;
        text-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
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
    st.markdown('<h1 class="main-header">♔ Chess Opening ROI Analyzer ♚</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Quantitative Finance Meets Chess Strategy</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 style="font-family: Cinzel, serif; color: #d4af37;">⚙️ Configuration</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
        <b>♟️ Analytical Framework:</b><br><br>
        This tool applies quantitative finance metrics to chess opening selection:
        <ul style="margin-top: 0.5rem;">
            <li><b>Sharpe Ratio:</b> Risk-adjusted returns</li>
            <li><b>ROI:</b> Return on investment</li>
            <li><b>Volatility:</b> Outcome consistency</li>
            <li><b>Information Ratio:</b> Excess returns vs benchmark</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
        st.markdown('<h3 style="font-family: Cinzel, serif; color: #d4af37;">📊 Data Source</h3>', unsafe_allow_html=True)
        
        if st.button("📥 Load Sample Data", use_container_width=True):
            with st.spinner("Loading sample data..."):
                if load_sample_data():
                    st.success("✓ Sample data loaded successfully!")
                else:
                    st.error("Sample data not found. Please fetch new data.")
        
        st.caption("Sample data: ~1000 games from Lichess")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Credit
        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; background: rgba(212, 175, 55, 0.1); border-radius: 8px;">
            <p style="font-family: 'Cinzel', serif; color: #d4af37; margin: 0; font-size: 0.9rem;">
                Built by<br>
                <a href="https://github.com/sohamgugale" style="color: #ffd700; text-decoration: none; font-weight: 600;">
                    Soham Gugale
                </a>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if not st.session_state.data_loaded:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; margin: 2rem 0;">
            <p style="font-family: 'Lora', serif; font-size: 1.3rem; color: #f0d9b5;">
                ♟️ Click <b style="color: #d4af37;">'Load Sample Data'</b> in the sidebar to begin analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Educational content with chess theme
        with st.expander("📚 Understanding Quantitative Chess Metrics", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="font-family: 'Lora', serif; line-height: 1.8;">
                
                <h4 style="font-family: 'Cinzel', serif; color: #d4af37;">Performance Metrics</h4>
                
                <b style="color: #f0d9b5;">📈 Expected Return</b><br>
                Your average score with this opening (1.0=win, 0.5=draw, 0.0=loss)<br>
                • <b>0.60</b> = Scoring 60% on average<br>
                • <b>0.50</b> = Breaking even<br>
                • <b>0.40</b> = Losing more than winning<br><br>
                
                <b style="color: #f0d9b5;">🎯 Win Rate</b><br>
                Percentage of decisive victories<br>
                • <b>50%</b> = Win half your games<br>
                • <b>35-45%</b> = Typical range<br>
                • Higher = More decisive play<br><br>
                
                <b style="color: #f0d9b5;">🔄 Draw Rate</b><br>
                Frequency of drawn games<br>
                • Higher at master level (2200+)<br>
                • Lower at club level (1200-1800)<br>
                • Opening-dependent characteristics<br><br>
                
                <b style="color: #f0d9b5;">📊 Volatility</b><br>
                Outcome consistency measure<br>
                • <b>Low (0.3-0.4)</b> = Stable results<br>
                • <b>High (0.5+)</b> = Unpredictable outcomes<br>
                
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style="font-family: 'Lora', serif; line-height: 1.8;">
                
                <h4 style="font-family: 'Cinzel', serif; color: #d4af37;">Risk-Adjusted Metrics</h4>
                
                <b style="color: #f0d9b5;">💎 Sharpe Ratio</b><br>
                Return per unit of risk<br>
                • <b>> 0.4</b> = Excellent risk-adjusted returns<br>
                • <b>0.2-0.4</b> = Good balance<br>
                • <b>< 0.2</b> = High risk relative to returns<br>
                • <b>Higher is better</b><br><br>
                
                <b style="color: #f0d9b5;">💰 ROI (Return on Investment)</b><br>
                Net profit/loss percentage<br>
                • <b>+30%</b> = Strong positive returns<br>
                • <b>0%</b> = Breaking even<br>
                • <b>-20%</b> = Losing proposition<br>
                • Win=+100%, Draw=0%, Loss=-100%<br><br>
                
                <b style="color: #f0d9b5;">📉 Information Ratio</b><br>
                Excess return over baseline<br>
                • Measures outperformance vs 50% benchmark<br>
                • Positive = Better than expected<br>
                • Higher = More efficient outperformance<br>
                
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick reference cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="strategy-card">
                <div class="strategy-title">🎓 For Beginners</div>
                <div class="strategy-subtitle">Focus on Win Rate and Expected Return</div>
                <div class="strategy-desc">
                    Pick openings where you score above 0.50. Don't worry about Sharpe ratios yet—focus on learning solid, straightforward openings.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="strategy-card">
                <div class="strategy-title">⚡ For Improvers</div>
                <div class="strategy-subtitle">Balance Sharpe Ratio with Win Rate</div>
                <div class="strategy-desc">
                    Find openings with good risk/reward balance. Look for Sharpe > 0.3 and consistent results (lower volatility).
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="strategy-card">
                <div class="strategy-title">🏆 For Advanced</div>
                <div class="strategy-subtitle">Optimize Sharpe Ratio and ROI</div>
                <div class="strategy-desc">
                    Maximize risk-adjusted returns. Target high Sharpe ratios, minimize volatility, and focus on efficiency over raw win rate.
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Data is loaded - show analysis
        tabs = st.tabs(["♔ Optimal Opening", "📊 Risk-Return Analysis", "🔍 Opening Deep Dive", "📈 Rating Trends"])
        
        with tabs[0]:
            st.markdown('<h2 style="font-family: Cinzel, serif; color: #d4af37; text-align: center;">♔ Recommended Opening for Your Rating</h2>', unsafe_allow_html=True)
            
            # Find rating bin
            rating_bins = st.session_state.df_metrics['rating_bin'].unique()
            user_bin = None
            for rb in rating_bins:
                low, high = map(int, rb.split('-'))
                if low <= user_rating <= high:
                    user_bin = rb
                    break
            
            if user_bin:
                df_user = st.session_state.df_metrics[
                    st.session_state.df_metrics['rating_bin'] == user_bin
                ].copy()
                
                optimal_opening = df_user.nlargest(1, optimization_metric).iloc[0]
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Opening name
                    st.markdown(f"""
                    <div class="opening-name">
                        {optimal_opening['opening_name']}<br>
                        <span style="font-size: 1.2rem; color: #f0d9b5;">({optimal_opening['opening_eco']})</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Key metrics
                    metric_cols = st.columns(4)
                    metric_cols[0].metric(
                        "Expected Return", 
                        f"{optimal_opening['expected_return']:.3f}",
                        help="Your average score: 1.0=win, 0.5=draw, 0.0=loss"
                    )
                    metric_cols[1].metric(
                        "Win Rate", 
                        f"{optimal_opening['win_rate']*100:.1f}%",
                        help="Percentage of decisive victories"
                    )
                    metric_cols[2].metric(
                        "Sharpe Ratio", 
                        f"{optimal_opening['sharpe_ratio']:.3f}",
                        help="Risk-adjusted returns. Higher is better"
                    )
                    metric_cols[3].metric(
                        "ROI", 
                        f"{optimal_opening['roi']:.1f}%",
                        help="Net profit/loss percentage"
                    )
                    
                    # Outcome distribution
                    viz = OpeningVisualizer()
                    fig_outcomes = viz.create_outcome_distribution(optimal_opening)
                    fig_outcomes.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#f0d9b5', family='Lora')
                    )
                    st.plotly_chart(fig_outcomes, use_container_width=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="info-box">
                    <b>📊 Statistical Summary</b><br><br>
                    <b>Sample Size:</b> {optimal_opening['total_games']} games<br><br>
                    <b>Volatility:</b> {optimal_opening['volatility']:.3f}<br>
                    <span style="font-size: 0.9rem; color: #c0c0c0;">(Lower = More consistent)</span><br><br>
                    <b>Information Ratio:</b> {optimal_opening['information_ratio']:.3f}<br>
                    <span style="font-size: 0.9rem; color: #c0c0c0;">(Excess return per unit risk)</span><br><br>
                    <b>Draw Rate:</b> {optimal_opening['draw_rate']*100:.1f}%
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get metric description
                    metric_descriptions = {
                        'sharpe_ratio': 'risk-adjusted returns',
                        'roi': 'ROI',
                        'win_rate': 'win rate'
                    }
                    metric_desc = metric_descriptions.get(optimization_metric, 'performance')
                    
                    metric_recommendations = {
                        'sharpe_ratio': 'optimal risk/reward balance',
                        'roi': 'maximum profitability',
                        'win_rate': 'highest win percentage'
                    }
                    metric_rec = metric_recommendations.get(optimization_metric, 'strong performance')
                    
                    st.markdown(f"""
                    <div class="metric-card">
                    <b>💡 Strategic Insight</b><br><br>
                    Based on {optimal_opening['total_games']} games at your rating level ({user_bin}), 
                    this opening offers the best {metric_desc} 
                    while maintaining acceptable risk levels.
                    <br><br>
                    <span style="color: #d4af37;">Recommended for players seeking {metric_rec}.</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ Insufficient data for your rating range. Try adjusting the rating slider.")
        
        # Tab 2: Risk-Return
        with tabs[1]:
            st.markdown('<h2 style="font-family: Cinzel, serif; color: #d4af37;">📊 Opening Risk-Return Profiles</h2>', unsafe_allow_html=True)
            
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
            fig_frontier.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(26,20,16,0.5)',
                font=dict(color='#f0d9b5', family='Lora')
            )
            st.plotly_chart(fig_frontier, use_container_width=True)
            
            st.markdown("""
            <div class="info-box">
            <b>📖 Chart Interpretation:</b><br>
            • <b>Y-axis (Expected Return):</b> Higher values indicate better performance<br>
            • <b>X-axis (Volatility):</b> Lower values indicate more consistent results<br>
            • <b>Top-left openings:</b> Optimal risk-adjusted returns (High return, Low volatility)<br>
            • <b>Hover</b> over points to see detailed statistics for each opening
            </div>
            """, unsafe_allow_html=True)
            
            # Sharpe ratio rankings
            st.markdown('<h3 style="font-family: Cinzel, serif; color: #d4af37; margin-top: 2rem;">🏆 Top Openings by Risk-Adjusted Return</h3>', unsafe_allow_html=True)
            fig_sharpe = viz.create_sharpe_ratio_bars(df_filtered, top_n=10)
            fig_sharpe.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(26,20,16,0.5)',
                font=dict(color='#f0d9b5', family='Lora')
            )
            st.plotly_chart(fig_sharpe, use_container_width=True)
        
        # Tab 3: Deep Dive
        with tabs[2]:
            st.markdown('<h2 style="font-family: Cinzel, serif; color: #d4af37;">🔍 Opening Deep Dive</h2>', unsafe_allow_html=True)
            
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
                # Opening name header
                st.markdown(f"""
                <div class="opening-name">
                    {opening_data.iloc[0]['opening_name']}<br>
                    <span style="font-size: 1rem; color: #f0d9b5;">Performance Across All Rating Ranges</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                avg_metrics = opening_data.mean(numeric_only=True)
                
                col1.metric("Avg Win Rate", f"{avg_metrics['win_rate']*100:.1f}%")
                col2.metric("Avg Sharpe Ratio", f"{avg_metrics['sharpe_ratio']:.3f}")
                col3.metric("Avg ROI", f"{avg_metrics['roi']:.1f}%")
                col4.metric("Total Games", f"{opening_data['total_games'].sum():.0f}")
                
                # Performance by rating
                viz = OpeningVisualizer()
                fig_rating = viz.create_rating_comparison(opening_data, selected_opening)
                fig_rating.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26,20,16,0.5)',
                    font=dict(color='#f0d9b5', family='Lora')
                )
                st.plotly_chart(fig_rating, use_container_width=True)
                
                # Detailed table
                st.markdown('<h3 style="font-family: Cinzel, serif; color: #d4af37; margin-top: 2rem;">📋 Detailed Statistics by Rating</h3>', unsafe_allow_html=True)
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
        with tabs[3]:
            st.markdown('<h2 style="font-family: Cinzel, serif; color: #d4af37;">📈 Performance Trends Across Rating Ranges</h2>', unsafe_allow_html=True)
            
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
                fig.update_traces(line_color='#d4af37', marker=dict(size=10, color='#ffd700'))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26,20,16,0.5)',
                    font=dict(color='#f0d9b5', family='Lora')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(
                    rating_agg,
                    x='rating_bin',
                    y='win_rate',
                    title='Average Win Rate by Rating',
                    markers=True
                )
                fig.update_traces(line_color='#228b22', marker=dict(size=10, color='#32cd32'))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(26,20,16,0.5)',
                    font=dict(color='#f0d9b5', family='Lora')
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Games distribution
            fig = px.bar(
                rating_agg,
                x='rating_bin',
                y='total_games',
                title='Total Games Analyzed by Rating Range',
                color='total_games',
                color_continuous_scale=['#b58863', '#d4af37', '#ffd700']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(26,20,16,0.5)',
                font=dict(color='#f0d9b5', family='Lora'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.markdown("""
    <div class="custom-footer">
        <p style="font-family: 'Playfair Display', serif; font-size: 1.1rem; margin-bottom: 0.5rem;">
            ♟️ Chess Opening ROI Analyzer ♟️
        </p>
        <p style="font-family: 'Lora', serif; font-size: 0.95rem;">
            Built by <a href="https://github.com/sohamgugale">Soham Gugale</a> | 
            Data from <a href="https://lichess.org">Lichess.org</a>
        </p>
        <p style="font-family: 'Cinzel', serif; font-size: 0.85rem; color: #c0c0c0; margin-top: 1rem; letter-spacing: 2px;">
            APPLYING QUANTITATIVE FINANCE TO CHESS STRATEGY
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
