import polars as pl


def displayClassification(data):
    ranks = ['Category', 'System']

    #загрузка и соединение категорезированных функций
    ctg = data.getRastCls()
    hierarchy = {}
    categories = ctg.select([pl.col(ranks[0]).unique().sort()]).to_series().to_list()
    for categoryName in categories:
        hierarchy[categoryName] = sorted(set(ctg.select([pl.col(ranks[1]).filter(pl.col(ranks[0]) == categoryName)]).to_series()))
    return hierarchy