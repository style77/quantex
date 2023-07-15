# Quantex

Powerful trading bot, based on ChatGPT sentiment analysis of news headlines.

## Motivation

The goal of this project is to create a trading bot that can make money on the stock market. The bot will be based on the sentiment analysis of news headlines. The sentiment analysis will be done by a [OpenAi's ChatGPT](https://chat.openai.com/) model that has been trained on a large corpus of data. The bot will use the sentiment analysis to predict the stock market and make trades accordingly. It is inspired by paper released by Alejandro Lopez-Lira and Yuehua Tang from University of Florida on april 6th 2023, named ["Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models"](https://arxiv.org/pdf/2304.07619.pdf)

## Installation

Quantex uses [Docker](https://www.docker.com/) to run. To install Docker, follow the instructions on [Docker's website](https://docs.docker.com/get-docker/). For ease of use [Docker-compose](https://docs.docker.com/compose/) is also used. To install docker-compose, follow the instructions on [docker-compose's website](https://docs.docker.com/compose/install/).

While development following tools are used:
- [Visual Studio Code](https://code.visualstudio.com/)
- [Git](https://git-scm.com/)
- [GitFlow](https://github.com/petervanderdoes/gitflow-avh)

- [Python 3.11](https://www.python.org/downloads/release/python-3110/)
- [Poetry](https://python-poetry.org/docs/)

- [PostgreSQL](https://www.postgresql.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

- [Flake8](https://flake8.pycqa.org/en/latest/)
- [Black](https://black.readthedocs.io/en/stable/)
- [Mypy](https://mypy.readthedocs.io/en/stable/)

- [TypeScript](https://www.typescriptlang.org/)
- [ESLint](https://eslint.org/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Prettier](https://prettier.io/)

and many, many more awesome tools.

## Setup

To setup the project, run the following commands:

```bash
# Clone the repository
git clone https://github.io/style77/quantex.git

# Change directory to the project
cd quantex

```

# Details

When you look at `.env.example` file you can see a lot of meaningless variables. In this section I want to explain them.
First in general is that, why is that project so huge, when it could just be one file with scraper, and maybe Telegram bot, the reason for that is that I want to make this project as modular as possible, so that it can be easily extended in the future. That's why it does contain API, Database, frontend, docker etc. Also making your own fullstack project is great way to learn and showoff.

Entire project structure is closed, which means that only getting access to the server will allow attacker to get access to all of the api keys, secrets etc.

## QUANTEX_INVESTMENT_HORIZON
If you look at the code, you can see that we are saving both short term and long term investment explanation, why is that variable then specified in `.env` file? Well, the reason is that we are then posting the results to Telegram channel, and posting all of the results would be too much. So we are posting only the results that are in the investment horizon specified in `.env` file. That way we can post only the results that are relevant to the channel.