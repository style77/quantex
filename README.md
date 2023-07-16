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

# Setup

To setup the project, run the following commands:

```bash
# Clone the repository
git clone https://github.io/style77/quantex.git

# Change directory to the project
cd quantex

```

Now it depends on you, how would you want to run project.

## Docker

To run project with docker, you need to have docker and docker compose installed. After that you can run the following command:

**Development version**
```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build 
```

**Production version**
```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build 
```

## Poetry

To run project with poetry, you need to have python 3.11 and poetry installed. After that you can run the following command:

*Following commends will only run API, that anyway won't work without database - to run **only database** you can run `docker-compose -f deploy/docker-compose.services.yml --project-directory . up --build`*
```bash
poetry install
```

```bash
poetry run python -m quantex
```

### PgAdmin

To access pgadmin, you need to start development version of docker compose. After that to get ip of the pgadmin dashboard, run the following command:

```bash
docker inspect pgadmin_container  | grep IPAddress.
```

The default email and password for pgadmin is `admin@admin.com root`.

## Migrations

To run migrations, you need to have python 3.11 and poetry installed. After that you can run the following command:

```bash
poetry run alembic upgrade head
```

Before that, it's recommended to change ip of the database in `.env` file to `0.0.0.0` (if you already got database running)

# Details

When you look at `.env.example` file you can see a lot of meaningless variables. In this section I want to explain them.
First in general is that, why is that project so huge, when it could just be one file with scraper, and maybe Telegram bot, the reason for that is that I want to make this project as modular as possible, so that it can be easily extended in the future. That's why it does contain API, Database, frontend, docker etc. Also making your own fullstack project is great way to learn and showoff.

Entire project structure is closed, which means that only getting access to the server will allow attacker to get access to all of the api keys, secrets etc.
Project is called a "bot", however it doesn't have any specific bot functionality, that's because it's bot for sending signals, not really trading bot. In future I might add trading bot functionality, but for now it's just a free signal bot.

### QUANTEX_INVESTMENT_HORIZON
If you look at the code, you can see that we are saving both short term and long term investment explanation, why is that variable then specified in `.env` file? Well, the reason is that we are then posting the results to Telegram channel, and posting all of the results would be too much. So we are posting only the results that are in the investment horizon specified in `.env` file. That way we can post only the results that are relevant to the channel.

# License

This project is licensed under the terms of the GNU GPLv3 license.

# Contributing

If you want to contribute to this project, please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# Authors

- **[Joachim Hodana](github.com/style77)** - _Initial work_ - [Quantex](github.com/style77/quantex)