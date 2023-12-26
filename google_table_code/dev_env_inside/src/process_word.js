
function test() {

    one = getWord()
    Logger.log(one)
    console.log(one.word, setResults({
        ...one,
        // "word": "split",
        "attempts": 5,
        "guessed": 1
    }))

    answs = getWord({ count: 3 })
    Logger.log(answs)

    for (let ans of answs) {
        console.log(ans.word, setResults({
            ...ans,
            "attempts": 5,
            "guessed": 1
        }))
    }

    one = getWords()
    Logger.log(one)
    console.log(one.word, setResults({
        ...one,
        // "word": "split",
        "attempts": 5,
        "guessed": 1
    }))

    answs = getWords({ count: 3 })
    Logger.log(answs)

    for (let ans of answs) {
        console.log(ans.word, setResults({
            ...ans,
            "attempts": 5,
            "guessed": 1
        }))
    }

    // i = 0
    // answers = {}
    // answrs = []
    // while (i < 100) {
    // ans = getWord()
    // Logger.log(ans)  
    //   answers[ans.word] = answers[ans.word] || 0
    //   answers[ans.word]++
    //   answrs.push(ans.word)
    //   i++
    // }
    // Logger.log(answers)
    // Logger.log(answrs)

}

// Получим все вопросы и поправим ID при необходимости
function getFullData() {
    const dataStart = 2
    var data = WordsSheet.getSheetValues(dataStart, 1, WordsSheet.getLastRow() - 1, WordsSheet.getLastColumn())
        .map((el, ind) => [...el, ind + dataStart])

    let ids = new Set(data.map(e => e[COLNAMES.id]))
    ids.delete("")
    if (ids.size != data.length) {
        const rowPosition = data[0].length - 1
        const idPosition = COLNAMES.id + 1
        let lastId = Math.max(...ids, 0) 
        ids = new Set()

        for (let row of data) {
            let row_id = row[COLNAMES.id]
            if (!row_id || ids.has(row_id)) {
                lastId += 1
                WordsSheet.getRange(row[rowPosition], idPosition).setValue(lastId)
                row[COLNAMES.id] = lastId
                row_id = lastId
            }
            ids.add(row_id)
        }
    }

    return data
}

function getWordsForQuestions(count, previously_asked) {
    var selectedWords = []

    var data = getFullData()
    var paSet = new Set(previously_asked)
    var notAsked = data.filter(el => !el[COLNAMES.id] || !paSet.has(el[COLNAMES.id]))

    var redline = new Date()
    redline.setHours(redline.getHours() - 1)
    var fresh = notAsked.filter(el => !el[COLNAMES.access] || el[COLNAMES.access] < redline)

    if (fresh.length >= count) {
        selectedWords = get_random_elements(fresh, count)
    } else {
        selectedWords = fresh
        let diff = count - selectedWords.length
        let swId = new Set(selectedWords.map(e => e[COLNAMES.id]))
        var notSelected = notAsked.filter(el => !swId.has(el[COLNAMES.id]))

        if (notSelected.length < diff) {
            selectedWords = [...selectedWords, ...notSelected]
            swId = new Set(selectedWords.map(e => e[COLNAMES.id]))
            while (selectedWords.length < count) {
                let word = data[Math.floor(Math.random() * data.length)]
                let w = word[COLNAMES.id]
                if (!swId.has(w)) {
                    selectedWords.push(word)
                    swId.add(w)
                }
            }
        } else {
            selectedWords = [...selectedWords, ...get_random_elements(notSelected, diff)]
        }
    }

    return selectedWords.map(w => packWordRow(w))
}

function packWordRow(wordRow) {
    const selected_index = wordRow[wordRow.length - 1]
    var word = { row: selected_index }

    for (var key in COLNAMES) {
        word[key] = wordRow[COLNAMES[key]]
    }

    // if (!wordRow[COLNAMES.id]) {
    //     let row = WordsSheet.getRange(selected_index, 1, 1, WordsSheet.getLastColumn())
    //     wordRow = row.getValues()[0]
    //     wordRow[COLNAMES.id] = Math.max(...getDataColumnValues(COLNAMES.id)) + 1
    //     wordRow[COLNAMES.access] = new Date()
    //     row.setValues([wordRow])
    // }
    // else {
    //     WordsSheet.getRange(selected_index, COLNAMES.access + 1).setValue(new Date())
    // }
    WordsSheet.getRange(selected_index, COLNAMES.access + 1).setValue(new Date())
    return word
}


// Выбрать несколько рандомных элементов из массива, опираясь на степень заучивания
function get_random_elements(arr, count) {
    const idxs = new Set();
    while (idxs.size < count) {
        let index = Math.floor(Math.random() * arr.length)
        let el = arr[index]
        let precision = el[COLNAMES.guessed] / (el[COLNAMES.attempts] || 1)
        let recall = el[COLNAMES.guessed] / (el[COLNAMES.asked] || 1)
        if (precision + recall < Math.random() * 2.1) {
            idxs.add(index)
        }
    }
    return Array.from(idxs).map(e => arr[e])

    // Старая реализация
    // data.sort((a, b) => (a[COLNAMES.asked] || 0) - (b[COLNAMES.asked] || 0))
    // let minimal = (data[0][COLNAMES.asked] || 0) + 1
    // data = data.filter(el => !el[COLNAMES.asked] || el[COLNAMES.asked] < minimal)
    // Было <=, решил пока брать самые неспрошенные
    // Работало плохо, спрашивало ток новые слова, а на старые забивало
    // В идеале вывести метрику, но есть проблема:
    // Опираться на верность ответов - забить на перу раз сразу угаданные
    // На количество запросов - забивать на старые
}