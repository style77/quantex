import traceback
from typing import List

import undetected_chromedriver as uc
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import os
import time
import logging
from dotenv import load_dotenv
import requests

from .listener import EventListener
from .telegram import TelegramBot

load_dotenv()
INTERVAL = int(os.getenv("QUANTEX_INTERVAL", 30))

listener = EventListener()
telegram_bot = TelegramBot(os.getenv("QUANTEX_TELEGRAM_BOT_API_KEY"))


def get_chromedriver_path():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    chromedriver_path = os.path.join(
        current_directory, "driver", "chromedriver"
    )
    return chromedriver_path


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


class NewsScraper:
    def __init__(self, user, password, edenai_key):
        self.URL = "https://newsfilter.io/latest/news"
        self.API_URL = "http://localhost:8000/api/news"
        self.API_SECRET = os.getenv("QUANTEX_SECRET_KEY")

        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.options = uc.ChromeOptions()
        self.options.add_argument("--headless")
        self.user = user
        self.password = password
        self.edenai_key = edenai_key

    def setup(self):
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
        self.driver.execute_cdp_cmd(
            "Network.setCacheDisabled", {"cacheDisabled": True}
        )

        self.driver.get(self.URL)

        self.logger.debug("Logging in")

        log = self.login(
            self.user,
            self.password,
        )

        self.logger.info("Login successful")
        self.logger.debug("Reloading page")

        self.driver.get(self.URL)

        if not log:
            self.logger.error("Login failed. Exiting.")
            raise Exception("Login failed")

    def login(self, email: str, password: str):
        """
        Logs in to a website using the provided email and password.

        Args:
            email (str): The email address used for logging in.
            password (str): The password used for logging in.

        Returns:
            bool: True if the login is successful, False otherwise.
        """
        try:
            login_form = self.driver.find_element(
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

    def analyze(self, ticker, term, headline):
        """
        Analyzes a given headline to determine if it is good or bad for the stock price of
        a given ticker in a specified term.

        Args:
            ticker (str): The ticker symbol of the stock.
            term (str): The term or time period for which the analysis is being done.
            headline (str): The headline to be analyzed.

        Returns:
            dict: A dictionary containing the analysis result, including the term, ticker,
            headline, explanation, and result.
        """
        url = "https://api.edenai.run/v2/text/chat"
        payload = {
            "providers": "openai",
            "text": f'Answer “YES” if good news, “NO” if bad news, or “UNKNOWN” \
                      if uncertain. Then elaborate with one short and \
                      concise sentence and split elaborate and result with dash\' "-". Is this headline good or bad for \
                      the stock price of {ticker} in the {term} term? Headline: {headline}',
            "chat_global_action": "Act as a financial expert. You are a financial expert \
                                   with stock recommendation experience.",
            "previous_history": [],
            "temperature": 0.0,
            "max_tokens": 150,
            "settings": {"openai": "gpt-3.5-turbo"},
        }
        headers = {
            "Authorization": f"Bearer {self.edenai_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(url, json=payload, headers=headers)
        data = r.json()["openai"]

        if "generated_text" not in data:
            if "error" in data:
                self.logger.error(f"Error: {data['error']}")
                if data["error"].get("type") == "ProviderLimitationError":
                    self.logger.error("Sleeping 30 seconds and retrying")
                    time.sleep(30)
                    return self.analyze(ticker, term, headline)
            self.logger.error(f"Invalid response: {data}")
            return

        result = data["generated_text"].split("-")[0].strip()
        if result == "UNKNOWN":
            result = "neutral"
        elif result == "YES":
            result = "positive"
        elif result == "NO":
            result = "negative"
        else:
            self.logger.error(f"Invalid result: {result}")
            return

        explanation = "".join(data["generated_text"].split("\n")[1:]).strip()

        return {
            "term": term,
            "ticker": ticker,
            "headline": headline,
            "explanation": explanation,
            "result": result,
        }

    def check_headline(self, ticker, headline):
        """
        Analyzes the given `headline` using the EdenAI API for sentiment analysis.

        Args:
            ticker (str): The ticker symbol of the stock.
            headline (str): The headline to be analyzed.

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
        """
        result_short = self.analyze(ticker, "short", headline)
        result_long = self.analyze(ticker, "long", headline)

        if not result_short or not result_long:
            self.logger.error("Invalid result")
            return

        return {
            "term": {
                "short": result_short["result"],
                "long": result_long["result"],
            },
            "ticker": ticker,
            "headline": headline,
            "explanation": {
                "short": result_short["explanation"],
                "long": result_long["explanation"],
            },
        }

    def check_for_unique(self, data):
        """
        Checks a list of dictionaries for unique values for a given key.

        Args:
            data (list): A list of dictionaries.

        Returns:
            list: A list of dictionaries containing unique values for the given key.
        """

        unique = []

        for item in data:
            r = requests.get(
                self.API_URL,
                params={
                    "headline": item["headline"],
                    "ticker": item["ticker"],
                },
                headers={
                    "x-secret": self.API_SECRET,
                },
            )

            if r.json()["count"] == 0:
                unique.append(item)

        return unique

    def insert_results(self, data: List[dict]):
        """
        Inserts the given data into the database.

        Args:
            data (list): A list of dictionaries containing the data to be inserted.

        Returns:
            (int): The number of items inserted.
        """
        for item in data:
            payload_short = {
                "term": "short",
                "result": item["term"]["short"],
                "ticker": item["ticker"],
                "headline": item["headline"],
                "explanation": item["explanation"]["short"],
            }
            payload_long = {
                "term": "long",
                "result": item["term"]["long"],
                "ticker": item["ticker"],
                "headline": item["headline"],
                "explanation": item["explanation"]["long"],
            }
            payloads = [payload_short, payload_long]

            headers = {
                "x-secret": self.API_SECRET,
            }

            for payload in payloads:
                requests.post(self.API_URL, json=payload, headers=headers)

        return len(data) * 2

    def scrape(self, with_a: bool = True):
        """
        Scrape the given webpage using the provided Selenium driver.

        Args:
            with_a (bool): Whether to scrape with the "a" tag or not.
            This is because of the different HTML structure of the website.

        Returns:
            list: A list of dictionaries containing the scraped data. Each dictionary
                contains the following keys:
                - timestamp (str): The timestamp of the article.
                - ticker (list): A list of tickers associated with the article.
                - headline (str): The headline of the article.
        """
        self.logger.info("Hard reloading newsfilter.io")

        self.logger.debug("Scraping newsfilter.io")

        # Get all the articles
        articles = self.driver.find_elements(
            By.XPATH, "/html/body/div/div[2]/div[4]/div/div/div/div"
        )

        results = []

        for index, article in enumerate(articles):
            # If the article has no ticker, skip it

            if with_a:
                tickers_element = article.find_elements(
                    By.XPATH,
                    f"//div[{index + 1}]/a/div/div[2]/div/span",
                )

                tickers = [ticker.text for ticker in tickers_element]
                tickers = tickers[:-1]
            else:
                try:
                    tickers = [
                        article.find_element(
                            By.XPATH,
                            f"//div[{index + 1}]/div/div/div[2]/div/span[1]",
                        ).text
                    ]
                except NoSuchElementException:
                    self.logger.debug("No tickers scraped")
                    continue

            if tickers:
                self.logger.info(f"Scraped tickers: {tickers}")

            if not tickers or " " in tickers or "" in tickers:
                self.logger.debug("No tickers scraped")
                continue

            timestamp = article.find_element(
                By.XPATH,
                f"//div[{index + 1}]/{'a' if with_a else 'div'}/div/div[1]/div/span",
            ).text

            self.logger.info(f"Scraped timestamp: {timestamp}")

            headline = article.find_element(
                By.XPATH,
                f"//div[{index + 1}]/{'a' if with_a else 'div'}/div/div[3]/div/span[1]",
            ).text

            self.logger.info(f"Scraped headline: {headline}")

            if not timestamp or not headline:
                self.logger.debug("Invalid timestamp or headline")
                continue

            try:
                datetime_obj = convert_relative_timestamp(timestamp)
            except ValueError:
                self.logger.debug("Invalid timestamp")
                continue

            data = {
                "timestamp": datetime_obj,
                "ticker": tickers,
                "headline": headline,
            }
            results.append(data)

        if len(results) > 0:
            self.logger.info(f"Scraped {len(results)} articles")
        else:
            self.logger.warning("No articles scraped")

        return results

    def run(self):
        try:
            with uc.Chrome(
                options=self.options,
                driver_executable_path=get_chromedriver_path(),
            ) as self.driver:
                self.setup()

                while True:
                    self.driver.execute_script("location.reload(true);")
                    time.sleep(4)

                    data = []

                    self.logger.info("Scraping with a tag")
                    d = self.scrape()
                    data.extend(d)

                    self.logger.info("Scraping without a tag")
                    d = self.scrape(with_a=False)
                    data.extend(d)

                    data = self.check_for_unique(data)

                    self.logger.info(
                        f"Found {len(data)} new articles"
                        if len(data) > 0
                        else "No new articles found"
                    )
                    if data:
                        results = []
                        for index, _item in enumerate(data):
                            self.logger.info(
                                f"Analyzing {index + 1}/{len(data)}"
                            )

                            ticker_list = _item["ticker"]
                            headline = _item["headline"]
                            for ticker in ticker_list:
                                result = self.check_headline(ticker, headline)
                                if not result:
                                    continue
                                results.append(result)

                                self.logger.info(
                                    "Sending result to telegram chat"
                                )
                                listener.call("unique_data", item=result)

                        self.logger.info("Inserting results into database")
                        self.insert_results(results)

                    self.logger.info(f"Sleeping for {INTERVAL} seconds")
                    telegram_bot.send_message(
                        os.getenv("QUANTEX_TELEGRAM_CHAT_ID"),
                        f"Sleeping until {time.strftime('%H:%M', time.localtime(time.time() + INTERVAL))}",
                    )
                    time.sleep(INTERVAL)
        except Exception as e:
            traceback.print_exc()
            self.logger.error("An error occurred: %s", str(e))


def preconfigure():
    """
    Initializes the necessary configurations for the program.

    This function retrieves the values of the environment variables "NEWSFILTER_USER",
    "NEWSFILTER_PASSWORD", and "EDENAI_API_KEY".
    It then checks if any of these values are missing and raises an Exception if so.

    Returns:
        Tuple[str, str, str]: A tuple containing the values of "NEWSFILTER_USER",
                              "NEWSFILTER_PASSWORD", and "EDENAI_API_KEY".

    Raises:
        Exception: If either the "NEWSFILTER_USER" or "NEWSFILTER_PASSWORD"
                   environment variables are missing.
        Exception: If the "EDENAI_API_KEY" environment variable is missing.
    """
    user = os.getenv("QUANTEX_NEWSFILTER_USER")
    password = os.getenv("QUANTEX_NEWSFILTER_PASSWORD")
    if not user or not password:
        raise Exception("Missing user or password")

    edenai_key = os.getenv("QUANTEX_EDENAI_API_KEY")
    if not edenai_key:
        raise Exception("Missing EdenAI API key")

    return user, password, edenai_key


@listener.on("unique_data")
def on_unique_data(item: list):
    payload_short = {
        "term": "short",
        "result": item["term"]["short"],
        "ticker": item["ticker"],
        "headline": item["headline"],
        "explanation": item["explanation"]["short"],
    }
    payload_long = {
        "term": "long",
        "result": item["term"]["long"],
        "ticker": item["ticker"],
        "headline": item["headline"],
        "explanation": item["explanation"]["long"],
    }
    payloads = [payload_short, payload_long]

    if (
        payload_long.get("result", "neutral") == "neutral"
        or payload_short.get("result", "neutral") == "neutral"
    ):
        return

    if payload_long["result"] == payload_short["result"]:
        payloads = [payload_long]

    for payload in payloads:
        message = f"*{payload['ticker']}* - {payload['headline']}\n\nResult: *{payload['result']}\n*Term: {payload['term']}\n\n"

        if payload["explanation"]:
            message += f"Explanation: {payload['explanation'].strip()[2:]}"

        r = telegram_bot.send_message(
            os.getenv("QUANTEX_TELEGRAM_CHAT_ID"), message
        )

        logging.info(r)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG
        if os.getenv("QUANTEX_ENVIRONMENT", "prod") == "dev"
        else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )

    _user, _password, _edenai_key = preconfigure()
    NewsScraper(_user, _password, _edenai_key).run()
