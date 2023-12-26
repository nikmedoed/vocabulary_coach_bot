function checkVersion() {
    return { version: "1.1" }
}


const METHODS = {
    get_word: getWord,
    get_words: getWords,
    set_result: setResults,
    check_version: checkVersion
}


function createOutput(data) {
    return ContentService.createTextOutput(JSON.stringify(data))
        .setMimeType(ContentService.MimeType.JSON)
    // .setHeaders({
    //   'Content-Type': 'application/json',
    //   'Access-Control-Allow-Origin': '*',
    //   'Access-Control-Allow-Methods': 'POST',
    //   'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept'
    // })
}


function doPost(e) {
    var raw = JSON.parse(e.postData.contents)
    try {
        return createOutput({ ok: METHODS[raw.method](raw.data) })
    } catch (err) {
        return createOutput({ error: "Глобальная ошибка базы", data: err })
    }
}


function doGet(e) {
    return doPost(e)
}