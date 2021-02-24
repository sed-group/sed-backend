FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /app

# Repo refresh
RUN sudo apt-get update

# Install additional deps
RUN pip install jose
RUN pip install -r requirements.txt
