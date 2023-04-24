FROM conda/miniconda3:latest
WORKDIR /app
COPY . .
RUN ["conda", "update", "-n", "base", "-c", "defaults", "conda"]  # Обновление conda
# CMD ["conda", "env", "create", "-f", "environment.yml"]  # Создание виртуального окружения conda
# CMD ["python", "FlaskApp/FlaskApp.py"]