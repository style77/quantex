import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import os
import time
import logging
from dotenv import load_dotenv
import requests

load_dotenv("../.env.local")

URL = "https://newsfilter.io/latest/news"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s || %(levelname)s || %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def convert_relative_timestamp(timestamp):
    """
    Convert a relative timestamp to a normal datetime.

    Args:
        timestamp (str): The relative timestamp to convert.

    Returns:
        datetime: The converted normal datetime.

    Raises:
        ValueError: If the timestamp unit is invalid.
    """
    timestamp = timestamp.replace(" ago", "")

    value = timestamp[:-1]
    unit = timestamp[-1]

    # Define the time delta based on the unit
    if unit == "s":
        delta = timedelta(seconds=int(value))
    elif unit == "m":
        delta = timedelta(minutes=int(value))
    elif unit == "h":
        delta = timedelta(hours=int(value))
    elif unit == "d":
        delta = timedelta(days=int(value))
    elif unit == "w":
        delta = timedelta(weeks=int(value))
    else:
        raise ValueError("Invalid timestamp unit")

    normal_datetime = datetime.now() - delta

    return normal_datetime


def login(driver: uc.Chrome, email: str, password: str):
    """
    Logs in to a website using the provided driver, email, and password.

    Args:
        driver (uc.Chrome): The web driver used to interact with the website.
        email (str): The email address used for logging in.
        password (str): The password used for logging in.

    Returns:
        bool: True if the login is successful, False otherwise.
    """
    try:
        login_form = driver.find_element(
            By.XPATH, "/html/body/div/div[2]/div[4]/div/div[1]/div"
        )
    except Exception:
        login_form = None

    if login_form:
        email_field = login_form.find_element(By.NAME, "email")
        email_field.send_keys(email)

        password_field = login_form.find_element(By.NAME, "password")
        password_field.send_keys(password)

        login_button = login_form.find_element(
            By.XPATH,
            "/html/body/div/div[2]/div[4]/div/div[1]/div/div[2]/ \
             div/div[3]/div[3]/button",
        )
        login_button.click()
        time.sleep(10)

    return True


def scrape(driver: uc.Chrome):
    """
    Scrape the given webpage using the provided Selenium driver.

    Args:
        driver (uc.Chrome): The Selenium driver used to scrape the webpage.

    Returns:
        list: A list of dictionaries containing the scraped data. Each dictionary
            contains the following keys:
            - timestamp (str): The timestamp of the article.
            - ticker (list): A list of tickers associated with the article.
            - headline (str): The headline of the article.
    """
    time.sleep(4)

    # Get all the articles
    articles = driver.find_elements(
        By.XPATH, "/html/body/div/div[2]/div[4]/div/div/div/div"
    )

    results = []

    for index, article in enumerate(articles):
        tickers_element = []
        # If the article has no ticker, skip it
        tickers_element = article.find_elements(
            By.XPATH,
            f"//div[{index+1}]/div/div/div[2]/div",
        )

        tickers = [
            ticker.find_element(By.XPATH, ".//*").text for ticker in tickers_element
        ]
        if not tickers or " " in tickers or "" in tickers:
            continue

        timestamp = article.find_element(
            By.XPATH,
            f"//div[{index + 1}]/div/div/div[1]/div/span",
        ).text

        headline = article.find_element(
            By.XPATH,
            f"//div[{index+1}]/div/div/div[3]/div/span[1]",
        ).text

        results.append(
            {
                "timestamp": convert_relative_timestamp(timestamp),
                "ticker": tickers,
                "headline": headline,
            }
        )

    return results


def preconfig():
    """
    Initializes the necessary configurations for the program.

    This function retrieves the values of the environment variables "NEWSFILTER_USER",
    "NEWSFILTER_PASSWORD", and "EDENAI_API_KEY".
    It then checks if any of these values are missing and raises an Exception if so.

    Returns:
        Tuple[str, str, str]: A tuple containing the values of "NEWSFILTER_USER",
        "NEWSFILTER_PASSWORD", and "EDENAI_API_KEY".

    Raises:
        Exception: If either the "NEWSFILTER_USER" or "NEWSFILTER_PASSWORD" environment
        variables are missing.
        Exception: If the "EDENAI_API_KEY" environment variable is missing.
    """
    user = os.getenv("NEWSFILTER_USER")
    password = os.getenv("NEWSFILTER_PASSWORD")
    if not user or not password:
        raise Exception("Missing user or password")

    edenai_key = os.getenv("EDENAI_API_KEY")
    if not edenai_key:
        raise Exception("Missing EdenAI API key")

    return user, password, edenai_key


def presetup(user, password):
    """
    Sets up the initial state of the function by performing the following steps:

    1. Opens the specified URL using the WebDriver instance.
    2. Calls the login function with the provided username and password to authenticate.
    3. Opens the same URL again using the WebDriver instance.
    4. Checks if the login was successful.
    5. Raises an exception if the login failed.

    Parameters:
    - user: The username to use for authentication (string).
    - password: The password to use for authentication (string).

    Raises:
    - Exception: If the login fails.

    Returns:
    - None
    """
    driver.get(URL)

    log = login(
        driver,
        user,
        password,
    )

    driver.get(URL)

    if not log:
        raise Exception("Login failed")


def analyze(ticker, term, headline, edenai_key):
    """
    Analyzes a given headline to determine if it is good or bad for the stock price of
    a given ticker in a specified term.

    Args:
        ticker (str): The ticker symbol of the stock.
        term (str): The term or time period for which the analysis is being done.
        headline (str): The headline to be analyzed.
        edenai_key (str): The API key for accessing the Eden AI service.

    Returns:
        dict: A dictionary containing the analysis result, including the term, ticker,
        headline, explanation, and result.
    """
    url = "https://api.edenai.run/v2/text/chat"
    payload = {
        "providers": "openai",
        "text": f"Answer “YES” if good news, “NO” if bad news, or “UNKNOWN” \
                  if uncertain in the first line. Then elaborate with one short and \
                  concise sentence on the next line. Is this headline good or bad for \
                  the stock price of {ticker} in the {term} term? Headline: {headline}",
        "chat_global_action": "Act as a financial expert. You are a financial expert \
                               with stock recommendation experience.",
        "previous_history": [],
        "temperature": 0.0,
        "max_tokens": 150,
        "settings": {"openai": "gpt-3.5-turbo"},
    }
    headers = {
        "Authorization": f"Bearer {edenai_key}",
        "Content-Type": "application/json",
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()["openai"]

    result = data["generated_text"].split("\n")[0]
    if result == "UNKNOWN":
        result = "neutral"
    elif result == "YES":
        result = "positive"
    elif result == "NO":
        result = "negative"
    else:
        logger.error("Invalid result: %s", result)
        return

    explanation = data["generated_text"].split("\n")[1:]

    return {
        "term": term,
        "ticker": ticker,
        "headline": headline,
        "explanation": explanation,
        "result": result,
    }


def check_headline(ticker, headline, edenai_key):
    """
    Analyzes the given `headline` using the EdenAI API for sentiment analysis.

    Args:
        ticker (str): The ticker symbol of the stock.
        headline (str): The headline to be analyzed.
        edenai_key (str): The API key for the EdenAI service.

    Returns:
        dict: A dictionary containing the analyzed results, including the sentiment
            scores and explanations.
            - term (dict): A dictionary containing the sentiment scores for both the
            short and long term.
                - short (float): The sentiment score for the short term.
                - long (float): The sentiment score for the long term.
            - ticker (str): The ticker symbol of the stock.
            - headline (str): The analyzed headline.
            - explanation (dict): A dictionary containing the explanations for both the
            short and long term sentiment scores.
                - short (str): The explanation for the short term sentiment score.
                - long (str): The explanation for the long term sentiment score.

    Raises:
        Exception: If the API returns an invalid result.
    """
    result_short = analyze(ticker, "short", headline, edenai_key)
    result_long = analyze(ticker, "long", headline, edenai_key)

    if not result_short or not result_long:
        raise Exception("Invalid result")

    return {
        "term": {
            "short": result_short["result"],
            "long": result_long["result"],
        },
        "ticker": ticker,
        "headline": headline,
        "explanation": {
            "short": result_short["explanation"][1],
            "long": result_long["explanation"][1],
        },
    }


if __name__ == "__main__":
    try:
        with uc.Chrome() as driver:
            user, password, edenai_key = preconfig()
            presetup(user, password)

            while True:
                data = scrape(driver)

                results = []
                for item in data:
                    ticker_list = item["ticker"]
                    headline = item["headline"]
                    for ticker in ticker_list:
                        result = check_headline(ticker, headline, edenai_key)
                        results.append(result)

                print(results)

                time.sleep(int(os.getenv("INTERVAL", 30)))
    except Exception as e:
        logger.error("An error occurred: %s", str(e))