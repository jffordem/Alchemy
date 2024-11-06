FROM python:3-slim

WORKDIR /app
COPY . /app
RUN pip install "poetry==1.1.4"
ENV PATH="/root/.poetry/bin:$PATH"
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
