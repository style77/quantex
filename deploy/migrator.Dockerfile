FROM python:3.9.6-slim-buster

# Install system dependencies
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.2.2

# Configure Poetry
RUN poetry config virtualenvs.create false

# Copy the project files
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Install project dependencies
RUN poetry install --no-dev

# Copy the rest of the application
COPY . /app/src/

# Set the entrypoint
CMD ["poetry", "run", "alembic", "upgrade", "head"]
