from typing import Annotated
import os

import wikipedia
import pandas as pd

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL


@tool
def wikipedia_tool(
    query: Annotated[
        str,
        "The Wikipedia search to execute to find key summary information."
    ],
):
    """Use this to search Wikipedia for factual information."""

    wikipedia.set_user_agent(
        "company-research-tool/1.0 "
        
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
            redirect=True
        )

    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"

    return (
        f"Successfully executed:\n"
        f"Wikipedia summary: {summary}"
    )


@tool
def stock_data_tool(
    company_ticker: Annotated[
        str,
        "The ticker symbol of the company to retrieve their stock performance data."
    ],
    num_days: Annotated[
        int,
        "The number of business days of stock data required to respond to the user query."
    ],
) -> str:
    """
    Use this to look-up stock performance data for companies.

    The data is retrieved from CSV files located in the data/ directory.
    """

    file_path = f"data/{company_ticker}.csv"

    if os.path.exists(file_path) is False:
        return (
            f"Sorry, but data for company {company_ticker} is not available. "
            "Please try Apple, Amazon, Meta, Microsoft, Netflix, or Tesla."
        )

    stock_df = pd.read_csv(
        file_path,
        index_col="Date",
        parse_dates=True
    )

    stock_df.index = stock_df.index.date

    max_num_days = (
        stock_df.index.max() - stock_df.index.min()
    ).days

    if num_days > max_num_days:
        return (
            "Sorry, but this time period exceeds the data available. "
            "Please reduce it to continue."
        )

    final_date = stock_df.index.max()

    filtered_df = stock_df[
        stock_df.index > (
            final_date - pd.Timedelta(days=num_days)
        )
    ]

    return (
        f"Successfully executed the stock performance data retrieval tool "
        f"to retrieve the last *{num_days} days* of data for company "
        f"**{company_ticker}**:\n\n"
        f"{filtered_df.to_markdown()}"
    )


# Python REPL
repl = PythonREPL()


@tool
def python_repl_tool(
    code: Annotated[
        str,
        "The python code to execute to generate your chart."
    ],
):
    """
    Use this to execute Python code.

    If you want to see the output of a value,
    use print(...).

    Charts should be displayed using plt.show().
    """

    try:
        result = repl.run(code)

    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"

    return (
        "Successfully executed the Python REPL tool.\n\n"
        "Python code executed:\n"
        f"```python\n{code}\n```\n\n"
        "Code output:\n"
        f"```\n{result}```"
    )