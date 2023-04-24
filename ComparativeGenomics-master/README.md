### Запуск докер-контейнера
```bash
docker build ./ComparativeGenomics-master/ -t test-polars-docker
docker run -p 5000:5000 -d -it test-polars-docker bash
```

### Установка библиотек
```bash 
conda install -c anaconda pandas 
conda install -c anaconda flask
conda install -c anaconda scikit-learn 
conda install -c conda-forge polars
conda install -c conda-forge pyarrow
conda install -c conda-forge scikit-bio
conda install -c plotly plotly
```