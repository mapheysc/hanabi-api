FROM sammaphey/hanabi-engine:1.0.0

WORKDIR /usr/src/app

COPY . .

RUN pip install -e .

EXPOSE 5000/tcp

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "--worker-class", "eventlet", "-w", "1", "launcher:rest.app"]