FROM python:3.11-slim

WORKDIR /app

COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn python-dotenv sqlalchemy asyncpg databases[postgresql] pydantic

EXPOSE 5001

ENV NAME World

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
