import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pytz
import ta
# test
# Set page config with dark theme
st.set_page_config(
    page_title="Real-Time Stock Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "Real-Time Stock Dashboard"
    }
)

# Apply dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1a1c24;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #31333f;
    }
    .stMarkdown {
        color: white;
    }
    h1, h2, h3 {
        color: white;
    }
    .metric-container {
        background-color: #1a1c24;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #9aa0b0;
        margin-top: 5px;
    }
    .metric-title {
        font-size: 1rem;
        color: #9aa0b0;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    .profit {
        color: #20ce99;
    }
    .loss {
        color: #ff5252;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: #1a1c24;
    }
    .sidebar-ticker {
        background-color: #1a1c24;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
    }
    .ticker-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .ticker-symbol {
        font-weight: bold;
        font-size: 1.2rem;
    }
    .ticker-price {
        font-weight: bold;
    }
    .dashboard-title {
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5rem;
        background: linear-gradient(90deg, #3a7bd5, #00d2ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    /* Custom button style */
    .stButton > button {
        background-color: #3a7bd5;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #2c5eb9;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stock-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .stock-symbol {
        font-size: 2.2rem;
        font-weight: 800;
    }
    .peer-stocks {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        margin-bottom: 25px;
    }
    .peer-stock-card {
        background-color: #1a1c24;
        border-radius: 8px;
        padding: 12px;
        min-width: 120px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .chart-container {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def format_number(num):
    """Format numbers with suffixes like K, M, B, T for better readability"""
    if num is None:
        return "N/A"
    
    magnitude = 0
    suffixes = ["", "K", "M", "B", "T"]
    while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        num /= 1000.0
    
    if magnitude > 0:
        return f"{num:.2f}{suffixes[magnitude]}"
    else:
        return f"{num:.2f}"

def get_stock_data(ticker, period="1y", interval="1d"):
    """Fetch stock data from Yahoo Finance"""
    stock = yf.Ticker(ticker)
    history = stock.history(period=period, interval=interval)
    
    if not history.empty:
        # Calculate additional metrics
        history['Date'] = history.index
        history['Change'] = history['Close'].pct_change() * 100
        history['Range'] = history['High'] - history['Low']
        
        # Add technical indicators
        history = add_technical_indicators(history)
    
    return stock, history

def add_technical_indicators(df):
    """Add technical indicators to the dataframe"""
    if df.empty:
        return df
    
    # Moving Averages
    df['SMA20'] = ta.trend.sma_indicator(df['Close'], window=20)
    df['SMA50'] = ta.trend.sma_indicator(df['Close'], window=50)
    df['SMA200'] = ta.trend.sma_indicator(df['Close'], window=200)
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    
    # RSI
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    
    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()
    
    # Bollinger Bands
    bollinger = ta.volatility.BollingerBands(df['Close'])
    df['BB_Upper'] = bollinger.bollinger_hband()
    df['BB_Lower'] = bollinger.bollinger_lband()
    df['BB_Mid'] = bollinger.bollinger_mavg()
    
    return df

def create_candlestick_chart(df, ticker, time_period, selected_indicators):
    """Create an interactive candlestick chart with technical indicators"""
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=2, 
        cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.8, 0.2],
        specs=[[{"secondary_y": True}],
               [{"secondary_y": False}]]
    )
    
    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name="Price",
            increasing_line_color='#26a69a', 
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # Add volume bar chart
    fig.add_trace(
        go.Bar(
            x=df.index, 
            y=df['Volume'],
            name='Volume',
            marker=dict(
                color='rgba(100, 100, 255, 0.5)',
            )
        ),
        row=2, col=1
    )
    
    # Add selected technical indicators
    if 'SMA20' in selected_indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA20'],
                name='SMA 20',
                line=dict(color='rgba(255, 255, 100, 0.8)', width=1.5)
            ),
            row=1, col=1
        )
    
    if 'SMA50' in selected_indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['SMA50'],
                name='SMA 50',
                line=dict(color='rgba(255, 100, 100, 0.8)', width=1.5)
            ),
            row=1, col=1
        )
    
    if 'EMA20' in selected_indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['EMA20'],
                name='EMA 20',
                line=dict(color='rgba(100, 255, 100, 0.8)', width=1.5)
            ),
            row=1, col=1
        )
    
    if 'BB' in selected_indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Upper'],
                name='BB Upper',
                line=dict(color='rgba(150, 150, 150, 0.5)', width=1),
                hoverinfo='skip'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['BB_Lower'],
                name='BB Lower',
                line=dict(color='rgba(150, 150, 150, 0.5)', width=1),
                fill='tonexty',
                fillcolor='rgba(150, 150, 150, 0.1)',
                hoverinfo='skip'
            ),
            row=1, col=1
        )
    
    if 'RSI' in selected_indicators:
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['RSI'],
                name='RSI',
                line=dict(color='#9C27B0', width=1.5)
            ),
            row=2, col=1
        )
        
        # Add RSI reference lines
        fig.add_hline(y=70, line_width=1, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_width=1, line_dash="dash", line_color="green", row=2, col=1)
    
    # Update layout
    fig.update_layout(
        title=f'{ticker} {time_period} Chart',
        xaxis_title='',
        yaxis_title='Price (USD)',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    # Update y-axis labels
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1)
    
    if 'RSI' in selected_indicators:
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    else:
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig

# Get popular tickers data for quick view
def get_popular_tickers_data():
    popular_tickers = ["AAPL", "GOOGL", "AMZN", "META", "MSFT", "TSLA", "NVDA", "JPM"]
    results = []
    
    for pticker in popular_tickers:
        try:
            pstock = yf.Ticker(pticker)
            pinfo = pstock.info
            pprice = pinfo.get('currentPrice', None)
            pchange = pinfo.get('regularMarketChange', 0)
            pchange_pct = pinfo.get('regularMarketChangePercent', 0) * 100
            
            results.append({
                "ticker": pticker,
                "price": pprice,
                "change": pchange,
                "change_pct": pchange_pct
            })
        except:
            pass
    
    return results

# Sidebar
with st.sidebar:
    st.title("Chart Parameters")
    
    # Ticker input
    st.subheader("Ticker")
    ticker = st.text_input("", value="AAPL", key="ticker_input").upper()
    
    # Time period selection
    st.subheader("Time Period")
    time_period = st.selectbox(
        "",
        options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "ytd", "max"],
        index=5
    )
    
    # Chart type
    st.subheader("Chart Type")
    chart_type = st.selectbox(
        "",
        options=["Candlestick", "Line", "OHLC"],
        index=0
    )
    
    # Technical indicators
    st.subheader("Technical Indicators")
    selected_indicators = st.multiselect(
        "",
        options=["SMA20", "SMA50", "EMA20", "BB", "RSI", "MACD"],
        default=["SMA20", "EMA20"]
    )
    
    # Update button
    update = st.button("Update", type="primary")

# Main dashboard
st.markdown("<h1 class=''>Real Time Stock Dashboard</h1>", unsafe_allow_html=True)

# Display popular tickers at the top
st.subheader("Market Overview")
popular_data = get_popular_tickers_data()

# Create columns for popular stocks
if popular_data:
    cols = st.columns(4)
    for i, stock_data in enumerate(popular_data):
        col_idx = i % 4
        with cols[col_idx]:
            price_color = "profit" if stock_data["change"] >= 0 else "loss"
            change_sign = "+" if stock_data["change"] >= 0 else ""
            
            # Create clickable ticker containers
            st.markdown(f"""
            <div class="metric-container" onclick="document.querySelector('#ticker_input').value='{stock_data['ticker']}'; document.querySelector('button[type=primary]').click();" style="cursor:pointer;">
                <div class="metric-title">{stock_data['ticker']}</div>
                <div class="metric-value">${stock_data['price']:.2f}</div>
                <div class="metric-label {price_color}">{change_sign}{stock_data['change']:.2f} ({change_sign}{stock_data['change_pct']:.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)

# Main content
if ticker:
    # Get stock data
    stock, history = get_stock_data(ticker, period=time_period)
    
    if not history.empty:
        # Get basic info
        info = stock.info
        current_price = info.get('currentPrice', history['Close'].iloc[-1])
        previous_close = info.get('previousClose', history['Close'].iloc[-2] if len(history) > 1 else None)
        
        # Calculate price change
        if previous_close:
            price_change = current_price - previous_close
            price_change_pct = (price_change / previous_close) * 100
        else:
            price_change = 0
            price_change_pct = 0
        
        # Stock header with company name
        company_name = info.get('shortName', ticker)
        st.markdown(f"""
        <div class="stock-header">
            <div class="stock-symbol">{ticker}</div>
            <div style="font-size: 1.5rem; opacity: 0.7;">{company_name}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            price_color = "profit" if price_change >= 0 else "loss"
            change_sign = "+" if price_change >= 0 else ""
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Last Price</div>
                <div class="metric-value">{current_price:.2f} USD</div>
                <div class="metric-label {price_color}">{change_sign}{price_change:.2f} ({change_sign}{price_change_pct:.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Day High</div>
                <div class="metric-value">{info.get('dayHigh', history['High'].max()):.2f} USD</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Day Low</div>
                <div class="metric-value">{info.get('dayLow', history['Low'].min()):.2f} USD</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            volume = info.get('volume', history['Volume'].iloc[-1])
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Volume</div>
                <div class="metric-value">{format_number(volume)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Market Cap</div>
                <div class="metric-value">{format_number(info.get('marketCap', 'N/A'))}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pe_ratio = info.get('trailingPE', 'N/A')
            pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">P/E Ratio</div>
                <div class="metric-value">{pe_display}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            div_yield = info.get('dividendYield', 0)
            div_display = f"{div_yield * 100:.2f}%" if div_yield else "N/A"
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">Dividend Yield</div>
                <div class="metric-value">{div_display}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            fifty_two_wk_high = info.get('fiftyTwoWeekHigh', 'N/A')
            fifty_two_wk_low = info.get('fiftyTwoWeekLow', 'N/A')
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-title">52-Week Range</div>
                <div class="metric-value">{fifty_two_wk_low if isinstance(fifty_two_wk_low, str) else f"{fifty_two_wk_low:.2f}"} - {fifty_two_wk_high if isinstance(fifty_two_wk_high, str) else f"{fifty_two_wk_high:.2f}"}</div>
            </div>
            """, unsafe_allow_html=True)
            
             # Show additional company information
        if 'longBusinessSummary' in info:
            with st.expander("Company Overview"):
                st.write(info['longBusinessSummary'])
                
                # Display additional company info in columns
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Sector:** " + info.get('sector', 'N/A'))
                    st.markdown("**Industry:** " + info.get('industry', 'N/A'))
                    st.markdown("**Country:** " + info.get('country', 'N/A'))
                
                with col2:
                    st.markdown("**Employees:** " + str(info.get('fullTimeEmployees', 'N/A')))
                    st.markdown("**Website:** " + info.get('website', 'N/A'))
                    st.markdown("**Exchange:** " + info.get('exchange', 'N/A'))
        
        # Create and display chart inside container
        st.markdown(f"<div class='chart-container'>", unsafe_allow_html=True)
        fig = create_candlestick_chart(history, ticker, time_period, selected_indicators)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
       
        
        # Display related stocks
        sector = info.get('sector', None)
        if sector:
            st.subheader(f"***Other {sector} Stocks***")
            # Get stocks in same sector
            sector_tickers = {
                "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
                "Healthcare": ["JNJ", "PFE", "UNH", "MRK", "ABBV"],
                "Finance": ["JPM", "BAC", "WFC", "C", "GS"],
                "Consumer": ["AMZN", "WMT", "PG", "KO", "MCD"],
                "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
                "Industrial": ["CAT", "HON", "MMM", "GE", "BA"]
            }
            
            related_tickers = sector_tickers.get(sector, [])[:5]
            related_tickers = [t for t in related_tickers if t != ticker]
            
            if related_tickers:
                cols = st.columns(len(related_tickers))
                
                for i, rel_ticker in enumerate(related_tickers):
                    try:
                        rel_stock = yf.Ticker(rel_ticker)
                        rel_info = rel_stock.info
                        rel_price = rel_info.get('currentPrice', None)
                        rel_change = rel_info.get('regularMarketChange', 0)
                        rel_change_pct = rel_info.get('regularMarketChangePercent', 0) * 100
                        
                        price_color = "profit" if rel_change >= 0 else "loss"
                        change_sign = "+" if rel_change >= 0 else ""
                        
                        with cols[i]:
                            st.markdown(f"""
                            <div class="metric-container" onclick="document.querySelector('#ticker_input').value='{rel_ticker}'; document.querySelector('button[type=primary]').click();" style="cursor:pointer;">
                                <div class="metric-title">{rel_ticker}</div>
                                <div class="metric-value">${rel_price:.2f}</div>
                                <div class="metric-label {price_color}">{change_sign}{rel_change:.2f} ({change_sign}{rel_change_pct:.2f}%)</div>
                            </div>
                            """, unsafe_allow_html=True)
                    except Exception as e:
                        with cols[i]:
                            st.error(f"Could not load data for {rel_ticker}")
    else:
        st.error(f"No data available for {ticker}")
else:
    st.info("Please enter a stock ticker in the sidebar and click Update to view stock information.")
