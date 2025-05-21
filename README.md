# Real-Time Stock Dashboard

A Streamlit-based financial dashboard that provides real-time stock data, interactive charts, and technical indicators.

## Project Structure

```
Real-Time-Stock/
├── .venv/                  # Virtual environment directory
├── main.py                 # Main Streamlit application script
├── requirements.txt        # Python package dependencies
└── README.md               # Project README file
```

## Features

- Real-time stock price tracking for user-defined tickers.
- Customizable time periods (1 day, 1 week, 1 month, 1 year, max).
- Choice of chart types: Candlestick or Line.
- Display of technical indicators: Simple Moving Average (SMA 20) and Exponential Moving Average (EMA 20).
- Key metrics display: Last Price, Change, % Change, High, Low, Volume.
- Interactive charts for visualizing stock performance.
- Historical data table display.
- Sidebar for easy parameter selection and real-time price updates for pre-selected stocks.
- Fetches data from Yahoo Finance (`yfinance`).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd Real-Time-Stock
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows:
    # .venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit app:**
    ```bash
    streamlit run zpp.py
    ```

## Usage

1.  Once the application is running, you will see a sidebar on the left and a main content area.
2.  **Sidebar - Chart Parameters:**
    *   **Ticker:** Enter the stock symbol you want to analyze (e.g., `AAPL`, `GOOGL`, `MSFT`). Default is `ADBE`.
    *   **Time Period:** Select the time frame for the data (e.g., `1d` for 1 day, `1wk` for 1 week).
    *   **Chart Type:** Choose between `Candlestick` or `Line` chart.
    *   **Technical Indicators:** Select one or more indicators to overlay on the chart (e.g., `SMA 20`, `EMA 20`).
    *   Click the **Update** button to refresh the chart and data based on your selections.
3.  **Sidebar - Real-Time Stock Prices:**
    *   This section displays the current price and change for a predefined list of stocks (`AAPL`, `GOOGL`, `AMZN`, `MSFT`).
4.  **Main Content Area:**
    *   **Metrics:** Displays the last closing price, change, percentage change, daily high, daily low, and volume for the selected ticker and time period.
    *   **Chart:** Shows the interactive stock chart based on your selections.
    *   **Historical Data:** A table displaying the Open, High, Low, Close, and Volume for the selected period.
    *   **Technical Indicators:** A table displaying the values of the selected technical indicators over time.
5.  **Sidebar - About:**
    *   Provides a brief description of the dashboard.

## Data Sources

-   Stock market data is sourced from [Yahoo Finance](https://finance.yahoo.com/) using the `yfinance` library.

## Contributing

1.  Fork the repository.
2.  Create a feature branch: `git checkout -b feature/your-feature-name`
3.  Commit your changes: `git commit -m 'Add some feature: your feature description'`
4.  Push to the branch: `git push origin feature/your-feature-name`
5.  Submit a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (if one exists, otherwise specify). 