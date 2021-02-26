FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY . /app

# Install additional deps
RUN pip install jose
RUN pip install -r requirements.txt
