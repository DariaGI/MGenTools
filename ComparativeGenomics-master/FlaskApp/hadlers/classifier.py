import polars as pl
from hadlers.keywordsClassifier import keywordsClassify
from hadlers.validator import validate

def rastClassify(data, table_to, table_to_index):
    rastCls = data.getRastCls()

    if match('Subsystem', rastCls, table_to, table_to_index) > 0:
        return True
    else:
        return False


def userClassify(data, table_to, table_to_index):
    if match('Function', data.getUserCls(), table_to, table_to_index) > 0:
        return True
    else:
        return False


def kwClassify(data, table_to, table_to_index):
    for value in table_to[table_to_index, 'Function'].split('; <br>'):
        keywordsClassify(value, data)
        match('Function', data.getKwCls(), table_to, table_to_index)


def match(match_type, table_from, table_to, table_to_index):
    matchCount = 0
    for value in table_to[table_to_index, match_type].split('; <br>'):
        table_from_indexes = table_from.filter(pl.col(match_type) == value.strip())
        if len(table_from_indexes) > 0:
            for row in table_from_indexes.rows():
                addRank('Category', table_to, table_from, table_to_index, row)
                addRank('System', table_to, table_from, table_to_index, row)
                matchCount += 1
                if match_type == 'Function':
                    addRank('Subsystem', table_to, table_from, table_to_index, row)
    return matchCount

def addRank(column, t_to, t_from, row_to, row):
    value = list(row)[t_from.columns.index(column)].strip()
    if 'none' in t_to[row_to, column] and len(t_to[row_to, column].split('; <br>')) <= 1:
        t_to[row_to, column] = value
    else:
        if t_to[row_to, column]:
            column_array = t_to[row_to, column].split(';')
            column_array = [j.strip() for j in column_array]
            if value not in column_array:
                column_array.append(value)
                t_to[row_to, column] = '; '.join(sorted(column_array))


def classifyFunctions(cls_types, files, data):
    resultsList = data.getClassified()
    displayError = ''

    for file in files:
        error, fileContent = validate(file, "rastDownload")
        if len(error) > 0:
            displayError = error
            continue
        if not {'System', 'Category'}.issubset(fileContent.columns):
            fileContent = fileContent.with_columns([pl.lit(pl.Series("System", ["none"], dtype=pl.Utf8))])
            fileContent = fileContent.with_columns([pl.lit(pl.Series("Category", ["none"], dtype=pl.Utf8))])
            fileContent = fileContent.select(['Category', 'System', 'Subsystem', 'Function'])

        classified = False
        if "0" in cls_types:
            fileContent_none = fileContent.filter(pl.col('Subsystem') == '- none -')
            fileContent = fileContent.filter(pl.col('Subsystem') != '- none -')

            for index in range(0, len(fileContent)):
                classified = rastClassify(data, fileContent, index)

            fileContent = pl.concat([fileContent, fileContent_none])

        elif "1" in cls_types and not classified:
            if not data.userCls.empty:
                for index in range(0, len(fileContent)):
                    classified = userClassify(data, fileContent, index)

        elif "2" in cls_types and not classified:
            for index in range(0, len(fileContent)):
                kwClassify(data, fileContent, index)

        filename = '.'.join(file.filename.split('.')[:-1])
        resultsList[filename] = fileContent

    return displayError, resultsList
