from nikolaik/python-nodejs:python3.11-nodejs18

WORKDIR /app

COPY bff /app/bff
COPY frontend /app/frontend
COPY requirements/llm.txt /app/requirements/bff.txt

WORKDIR /app/frontend
RUN npm ci
RUN npm run build

WORKDIR /app
RUN pip install eventlet
RUN pip install python-socketio[client]

CMD ["python", "bff/main.py"]

