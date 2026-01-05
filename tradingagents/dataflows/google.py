from typing import Annotated
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .googlenews_utils import getNewsData


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"] = None,
) -> str:
    """Get news from Google News.

    Supports two call signatures:
    1. (query, curr_date, look_back_days) - original format
    2. (ticker, start_date, end_date) - for compatibility with news routing
    """
    query = query.replace(" ", "+")

    # Handle both call signatures
    if look_back_days is None or isinstance(look_back_days, str):
        # Called with (ticker, start_date, end_date) format
        start_date_str = curr_date  # This is actually start_date
        end_date_str = look_back_days if look_back_days else curr_date  # This is actually end_date

        try:
            start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else datetime.now()
            before = start_date_str
            curr_date = end_date_str or datetime.now().strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            # Fallback to default 7-day lookback
            end_dt = datetime.now()
            start_dt = end_dt - relativedelta(days=7)
            before = start_dt.strftime("%Y-%m-%d")
            curr_date = end_dt.strftime("%Y-%m-%d")
    else:
        # Original format: (query, curr_date, look_back_days)
        end_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        before = (end_dt - relativedelta(days=int(look_back_days))).strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"