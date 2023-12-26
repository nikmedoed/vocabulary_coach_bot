// Получить словарь заголовок - индекс
function getHeaders() {
    var ColNames = {}
    WordsSheet.getSheetValues(1, 1, 1, WordsSheet.getLastColumn())[0].map((el, ind) => {
        ColNames[el] = ind
    })
    return ColNames
}


// Получить словарь понтный боту атрибут - индекс колонки
function getColNames(attributes_to_columns_names) {
    var ColNames = getHeaders()
    if (ColNames.id == null) {
        WordsSheet.insertColumnBefore(1)
        let range = WordsSheet.getRange(1, 1, WordsSheet.getLastRow(), 1)
        let values = range.getValues()
        values[0][0] = 'id'
        for (let i = 1; i < values.length; i++) {
            values[i][0] = i
        }
        range.setValues(values)
        WordsSheet.autoResizeColumn(1)
        WordsSheet.hideColumns(1)
        var ColNames = getHeaders()
    }
    for (var key in attributes_to_columns_names) {
        attributes_to_columns_names[key] = ColNames[attributes_to_columns_names[key]]
    }
    return attributes_to_columns_names
}


// ориентированный на legacy специфику бота, чтобы не возвращать массив, когда элемент один
function retrunFix(arr) {
    return arr.length == 1 ? arr[0] : arr
}


// Получить полный столбец значений
function getDataColumnValues(id) {
    return WordsSheet.getSheetValues(2, id + 1, WordsSheet.getLastRow() - 1, 1).map((el) => el[0])
}


// Перемешать элементы в массиве
function shuffle(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1))
        let t = array[i]; array[i] = array[j]; array[j] = t
    }
    return array
}