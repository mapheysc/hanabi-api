FROM python:3.7

COPY . .

RUN pip install -e .
RUN pip install hanaby

ENTRYPOINT [ "hanabi", "-s", "-l", "DEBUG" ]