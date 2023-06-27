FROM conda/miniconda3:latest
WORKDIR /app
COPY . .
RUN ["conda", "update", "-n", "base", "-c", "defaults", "conda"] 
