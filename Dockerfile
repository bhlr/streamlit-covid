FROM python:3.7.2-slim
LABEL maintainer="Byron Linares"

EXPOSE 8501

WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install streamlit
RUN pip install -r requirements.txt

COPY ./src /src
ENTRYPOINT [ "streamlit", "run"]
CMD ["/src/app.py"]
