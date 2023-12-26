function getHeaders() {
  var ColNames = {}
  Sheet.getSheetValues(1, 1, 1, Sheet.getLastColumn())[0].map((el, ind) => {
    ColNames[el] = ind
  })
  return ColNames
}

function getColNames() {
  var COLNAMES = {
    word: "Ответ",
    question: "Вопрос (пояснение)",
    hint: "Подсказка",
    asked: "Задано раз",
    attempts: "Попыток",
    guessed: "Угадано",
    access: "Последний раз задано",
    id: 'id'
  }
  var ColNames = getHeaders()
  if (ColNames.id == null) {
    Sheet.insertColumnBefore(1)
    let range = Sheet.getRange(1, 1, Sheet.getLastRow(), 1)
    let values = range.getValues()
    values[0][0] = 'id'
    for (let i = 1; i < values.length; i++) {
      values[i][0] = i
    }
    range.setValues(values)
    Sheet.autoResizeColumn(1)
    Sheet.hideColumns(1)
    var ColNames = getHeaders()
  }
  for (var key in COLNAMES) {
    COLNAMES[key] = ColNames[COLNAMES[key]]
  }
  return COLNAMES
}


function createOutput(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON)
    .setHeaders({
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST',
      'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept'
    })
}


function doPost(e) {
  var raw = JSON.parse(e.postData.contents)
  try {
    return createOutput({ ok: METHODS[raw.method](raw.data) })
  } catch (err) {
    return createOutput({ error: "Глобальная ошибка базы", data: err })
  }
  // switch (raw.method) {
  //   case "get_word":
  //     return createOutput({ ok:  })
  //   case "get_words":
  //     return createOutput({ ok: getWords() })
  //   case "set_result":
  //     return createOutput({ ok: setResults(raw.data) })
  //   default:
  //     return createOutput({ error: "Глобальная ошибка базы" })
  // }
}


function doGet(e) {
  return doPost(e)
}