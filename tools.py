from typing import Annotated
import os

import requests
import wikipedia
import pandas as pd
import matplotlib

# Use a non-GUI backend because this runs inside a Gradio/server environment.
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Wikipedia Tool
# =========================================================

@tool
def wikipedia_tool(
    query: Annotated[
        str,
        "The Wikipedia search to execute to find key summary information."
    ],
):
    """
    Search Wikipedia and return a concise factual summary.
    """

    wikipedia.set_user_agent(
        "company-research-tool/1.0"
    )

    try:
        results = wikipedia.search(query)

        if not results:
            return "No results found on Wikipedia."

        title = results[0]

        summary = wikipedia.summary(
            title,
            sentences=8,
            auto_suggest=False,
            redirect=True,
        )

        return (
            f"Successfully executed Wikipedia search.\n\n"
            f"Title: {title}\n\n"
            f"Summary:\n{summary}"
        )

    except Exception as e:
        return (
            f"Failed to execute Wikipedia search.\n"
            f"Error: {repr(e)}"
        )


# =========================================================
# Alpha Vantage Stock Data
# =========================================================

def get_stock_data(
    company_ticker: str,
    num_days: int,
) -> pd.DataFrame | str:
    """
    Retrieve recent daily stock data from Alpha Vantage.

    Parameters
    ----------
    company_ticker : str
        Stock ticker such as AAPL, MSFT, AMZN, TSLA.

    num_days : int
        Number of recent trading days required.

    Returns
    -------
    pd.DataFrame
        Recent trading-day OHLCV data.

    str
        Error message if data cannot be retrieved.
    """

    # -----------------------------------------------------
    # Validate inputs
    # -----------------------------------------------------

    company_ticker = company_ticker.upper().strip()

    if not company_ticker:
        return "Stock ticker cannot be empty."

    if num_days <= 0:
        return "num_days must be greater than 0."

    # -----------------------------------------------------
    # Get API key
    # -----------------------------------------------------

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        return (
            "ALPHA_VANTAGE_API_KEY is not configured. "
            "Add it to your .env file."
        )

    # -----------------------------------------------------
    # Alpha Vantage API
    # -----------------------------------------------------

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": company_ticker,
        "outputsize": "compact",
        "apikey": api_key,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=20,
        )

        response.raise_for_status()

    except requests.RequestException as e:
        return (
            f"Failed to retrieve stock data for "
            f"{company_ticker}.\n"
            f"Error: {repr(e)}"
        )

    # -----------------------------------------------------
    # Parse JSON
    # -----------------------------------------------------

    try:
        data = response.json()

    except ValueError:
        return (
            "Alpha Vantage returned an invalid response."
        )

    # -----------------------------------------------------
    # Handle Alpha Vantage errors
    # -----------------------------------------------------

    if "Error Message" in data:
        return (
            f"Invalid or unsupported stock ticker: "
            f"{company_ticker}."
        )

    if "Note" in data:
        return (
            "Alpha Vantage API request limit was reached.\n\n"
            f"Message: {data['Note']}"
        )

    if "Information" in data:
        return (
            "Alpha Vantage returned an information message "
            "instead of stock data.\n\n"
            f"Message: {data['Information']}"
        )

    # -----------------------------------------------------
    # Extract daily time series
    # -----------------------------------------------------

    time_series = data.get("Time Series (Daily)")

    if not time_series:

        return (
            f"No daily stock data was returned for "
            f"{company_ticker}.\n\n"
            f"Alpha Vantage response keys: "
            f"{list(data.keys())}"
        )

    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    stock_df = pd.DataFrame.from_dict(
        time_series,
        orient="index",
    )

    # Convert dates
    stock_df.index = pd.to_datetime(
        stock_df.index,
        errors="coerce",
    )

    # Remove invalid dates
    stock_df = stock_df[
        stock_df.index.notna()
    ]

    # -----------------------------------------------------
    # Rename columns
    # -----------------------------------------------------

    stock_df = stock_df.rename(
        columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume",
        }
    )

    # -----------------------------------------------------
    # Convert values to numeric
    # -----------------------------------------------------

    for column in [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]:
        if column in stock_df.columns:
            stock_df[column] = pd.to_numeric(
                stock_df[column],
                errors="coerce",
            )

    # -----------------------------------------------------
    # Sort chronologically
    # -----------------------------------------------------

    stock_df = stock_df.sort_index()

    # -----------------------------------------------------
    # Remove rows with missing close prices
    # -----------------------------------------------------

    stock_df = stock_df.dropna(
        subset=["Close"]
    )

    if stock_df.empty:
        return (
            f"Stock data for {company_ticker} "
            f"contained no valid closing prices."
        )

    # -----------------------------------------------------
    # Get most recent N TRADING DAYS
    # -----------------------------------------------------

    if num_days > len(stock_df):
        return (
            f"Only {len(stock_df)} trading days are "
            f"available for {company_ticker}, but "
            f"{num_days} were requested."
        )

    stock_df = stock_df.tail(num_days)

    return stock_df


# =========================================================
# Stock Data Tool
# =========================================================

@tool
def stock_data_tool(
    company_ticker: Annotated[
        str,
        """
        Stock ticker symbol.

        Examples:
        Apple = AAPL
        Microsoft = MSFT
        Amazon = AMZN
        Meta = META
        Netflix = NFLX
        Tesla = TSLA
        """,
    ],
    num_days: Annotated[
        int,
        """
        Number of recent trading days required.

        Examples:
        10 = last 10 trading days
        20 = last 20 trading days
        30 = last 30 trading days
        """,
    ],
) -> str:
    """
    Retrieve recent stock performance data.

    This tool returns daily OHLCV stock data that can then
    be analyzed by the Analyst Agent using Python.
    """

    company_ticker = company_ticker.upper().strip()

    stock_df = get_stock_data(
        company_ticker,
        num_days,
    )

    # -----------------------------------------------------
    # Handle errors
    # -----------------------------------------------------

    if isinstance(stock_df, str):
        return stock_df

    # -----------------------------------------------------
    # Dates
    # -----------------------------------------------------

    earliest_date = stock_df.index.min().strftime(
        "%Y-%m-%d"
    )

    latest_date = stock_df.index.max().strftime(
        "%Y-%m-%d"
    )

    # -----------------------------------------------------
    # Basic statistics
    # -----------------------------------------------------

    highest_close = stock_df["Close"].max()

    lowest_close = stock_df["Close"].min()

    average_close = stock_df["Close"].mean()

    # -----------------------------------------------------
    # Return clean information to the agent
    # -----------------------------------------------------

    return (
        f"Successfully retrieved stock data for "
        f"{company_ticker}.\n\n"

        f"Period: {earliest_date} → {latest_date}\n"
        f"Trading days: {len(stock_df)}\n\n"

        f"Basic statistics:\n"
        f"- Highest closing price: "
        f"{highest_close:.2f}\n"
        f"- Lowest closing price: "
        f"{lowest_close:.2f}\n"
        f"- Average closing price: "
        f"{average_close:.2f}\n\n"

        f"Daily stock data:\n\n"
        f"{stock_df.to_markdown()}"
    )


# =========================================================
# Python REPL
# =========================================================

repl = PythonREPL()


# =========================================================
# Python Execution Tool
# =========================================================

@tool
def python_repl_tool(
    code: Annotated[
        str,
        """
        Python code to execute.

        Use this tool for:
        - calculations
        - statistics
        - data analysis
        - visualization
        - charts
        """,
    ],
):
    """
    Execute Python code for analysis and visualization.

    The Analyst Agent generates the Python code.
    This tool executes that code.
    """

    try:

        # -------------------------------------------------
        # Execute Python
        # -------------------------------------------------

        result = repl.run(code)

        # -------------------------------------------------
        # Check whether matplotlib created figures
        # -------------------------------------------------

        figure_paths = []

        figure_numbers = plt.get_fignums()

        if figure_numbers:

            os.makedirs(
                "outputs",
                exist_ok=True,
            )

            for i, figure_number in enumerate(
                figure_numbers,
                start=1,
            ):

                figure = plt.figure(
                    figure_number
                )

                image_path = os.path.abspath(
                    f"outputs/plot_{figure_number}.png"
                )

                figure.savefig(
                    image_path,
                    bbox_inches="tight",
                    dpi=150,
                )

                figure_paths.append(
                    image_path
                )

            # Close figures after saving
            plt.close("all")

        # -------------------------------------------------
        # Build response
        # -------------------------------------------------

        response = (
            "Successfully executed the Python REPL tool.\n\n"
            "Python code executed:\n"
            "```python\n"
            f"{code}\n"
            "```\n\n"
            "Code output:\n"
            "```\n"
            f"{result}\n"
            "```\n"
        )

        # -------------------------------------------------
        # Add generated image information
        # -------------------------------------------------

        if figure_paths:

            response += (
                "\nGenerated visualization(s):\n"
            )

            for path in figure_paths:
                response += (
                    f"IMAGE_PATH: {path}\n"
                )

        return response

    except Exception as e:

        return (
            "Failed to execute Python code.\n"
            f"Error: {repr(e)}"
        )