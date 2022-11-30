FROM python:3.8
LABEL maintainer="Amer Osmanovic"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py
CMD ["python", "app.py"]
EXPOSE 3111