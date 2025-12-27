# ♟️ Chess Opening ROI Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chess-opening-analyser.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Applying Financial Analytics to Chess Strategy**

A professional chess analytics platform that applies quantitative finance metrics (ROI, Sharpe ratio, risk-return optimization) to chess opening selection. Think of it as portfolio optimization for chess openings.

**Live Demo**: [Try it here →](https://chess-opening-analyser.streamlit.app)

---

## 🎯 What Makes This Unique?

Traditional chess analysis focuses on engine evaluations. This project treats chess openings like **financial instruments**, analyzing them through:

- **Expected Return**: Average points scored (Win=1.0, Draw=0.5, Loss=0.0)
- **Volatility**: Consistency of outcomes (standard deviation)
- **Sharpe Ratio**: Risk-adjusted performance metric
- **ROI (Return on Investment)**: Net gains considering risk
- **Efficient Frontier**: Risk-return optimization curves

---

## ✨ Key Features

### 📊 Financial Metrics Applied to Chess
- **Sharpe Ratio Calculation**: Measure risk-adjusted returns for each opening
- **ROI Analysis**: Calculate return on investment per opening
- **Volatility Measurement**: Assess outcome consistency
- **Information Ratio**: Evaluate excess returns relative to benchmark

### 🎯 Personalized Recommendations
- Rating-specific opening suggestions (800-2800 rating range)
- Optimization by different objectives (max Sharpe, max ROI, max win rate)
- Sample size filtering for statistical reliability

### 📈 Interactive Visualizations
- **Efficient Frontier**: Risk-return scatter plots (like stock portfolios)
- **Sharpe Ratio Rankings**: Top openings by risk-adjusted returns
- **Outcome Distributions**: Win/draw/loss pie charts
- **Rating Trend Analysis**: Performance across skill levels

### 🔍 Deep Analysis Tools
- Opening performance by rating ranges
- Cross-rating comparison charts
- Detailed statistical breakdowns
- Educational tooltips explaining financial concepts

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **Data Source** | Lichess.org API |
| **Analysis** | Pandas, NumPy, SciPy |
| **Visualization** | Plotly (interactive charts) |
| **Web Framework** | Streamlit |
| **Chess Engine** | python-chess library |

---

## 📁 Project Structure
```
chess-opening-analyser/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── data/
│   ├── raw/                       # Raw data from Lichess
│   └── processed/                 # Cleaned datasets
│       └── sample_games.csv       # Sample data for demo
├── src/
│   ├── utils/
│   │   └── data_fetcher.py       # Lichess API integration
│   ├── analysis/
│   │   └── roi_calculator.py     # Financial metrics engine
│   └── visualization/
│       └── charts.py              # Plotly chart generators
└── notebooks/
    └── generate_sample_data.py    # Sample data generator
```

---

## 🚀 Installation & Usage

### Quick Start
```bash
# Clone repository
git clone https://github.com/sohamgugale/chess-opening-analyser.git
cd chess-opening-analyser

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

### Using the App

1. **Set Your Rating**: Use the slider in the sidebar (800-2800 range)
2. **Choose Optimization Goal**: Select Sharpe ratio, ROI, or win rate
3. **Load Data**: Click "Load Sample Data" to analyze ~1000+ sample games
4. **Explore**:
   - **Recommendations**: See optimal openings for your rating
   - **Risk-Return**: Visualize efficient frontier
   - **Deep Dive**: Analyze specific openings across rating ranges
   - **Trends**: Compare performance patterns

---

## 📊 Methodology

### Financial Metrics Explained

#### Expected Return
```
E[R] = (Wins × 1.0) + (Draws × 0.5) + (Losses × 0.0) / Total Games
```
Average points scored per game (chess analog of investment returns).

#### Volatility (Risk)
```
σ = √[Σ(Returns - Mean)² / N]
```
Standard deviation of outcomes (measures consistency).

#### Sharpe Ratio (Risk-Adjusted Return)
```
Sharpe = (E[R] - Rf) / σ
```
Where Rf = 0.5 (draw rate as "risk-free" rate). Measures excess return per unit of risk.

#### ROI (Return on Investment)
```
ROI = [(Wins × 100%) + (Draws × 0%) + (Losses × -100%)] / Total Games
```
Net percentage return treating wins as 100% gains, losses as 100% losses.

---

## 📈 Sample Results

### Example Analysis (1600-1800 Rating Range)

| Opening | Sharpe Ratio | Win Rate | ROI | Volatility |
|---------|-------------|----------|-----|-----------|
| Italian Game (C50) | 0.234 | 48.2% | 21.5% | 0.42 |
| Sicilian Defense (B20) | 0.187 | 45.3% | 16.2% | 0.44 |
| French Defense (C00) | 0.156 | 43.1% | 13.4% | 0.46 |

**Insight**: Italian Game offers best risk-adjusted returns at this level.

---

## 🎓 Key Learnings & Skills Demonstrated

### Quantitative Analysis
- Applied portfolio theory to non-financial domain
- Statistical modeling of competitive performance
- Risk-return optimization frameworks

### Data Engineering
- API integration (Lichess)
- Data preprocessing and cleaning
- Efficient data structure design

### Visualization
- Interactive dashboard development
- Financial chart types (efficient frontier, risk metrics)
- Educational UI/UX design

### Business Application
- Personalized recommendation systems
- Rating-based segmentation
- Decision support tools

---

## 🔮 Future Enhancements

- [ ] **Real-time Data**: Live Lichess API integration
- [ ] **Machine Learning**: Predict opening success based on player style
- [ ] **Position Analysis**: Extend to mid-game positions
- [ ] **Multi-objective Optimization**: Pareto frontier for multiple goals
- [ ] **Opening Repertoire Builder**: Suggest complementary opening systems
- [ ] **Tournament Preparation**: Opponent-specific analysis
- [ ] **Time Control Segmentation**: Separate analysis for blitz/rapid/classical

---

## 📚 Data Sources & Acknowledgments

- **Lichess.org**: Open chess database and API
- **Chess.com**: Opening theory references
- **Modern Portfolio Theory**: Markowitz framework inspiration
- **Quantitative Finance Literature**: Sharpe, Sortino ratio concepts

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional chess platforms (Chess.com API)
- Advanced financial metrics (Sortino ratio, maximum drawdown)
- Machine learning models
- UI/UX enhancements

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 👤 Author

**Soham Gugale**

- GitHub: [@sohamgugale](https://github.com/sohamgugale)
- LinkedIn: [Soham Gugale](https://linkedin.com/in/sohamgugale)
- Portfolio: [View Projects](https://github.com/sohamgugale)

---

## ⚠️ Disclaimer

This tool is for educational and analytical purposes. Chess performance depends on many factors beyond opening selection. Use insights as guidance, not guarantees.

---

**⭐ If this project helps your chess or career, please star the repository!**

*Built with ♟️ for the intersection of chess and quantitative analysis*
