function setResults(results) {
    let wordIndex = -1

    if (results.id) {
        results.id = parseInt(results.id)
        wordIndex = getDataColumnValues(COLNAMES.id).indexOf(results.id)
    }
    if (wordIndex == -1 || WordsSheet.getSheetValues(2 + wordIndex, COLNAMES.word + 1, 1, 1)[0] != results.word) {
        wordIndex = getDataColumnValues(COLNAMES.word).indexOf(results.word)
    }

    if (wordIndex == -1) {
        return { error: `No such word :: ${results.word}` }
    }
    wordIndex += 2

    let changes = [COLNAMES.attempts, COLNAMES.guessed, COLNAMES.asked]
    let min = Math.min(...changes) + 1
    let max = Math.max(...changes) + 1
    let shift = 1 - min

    var range = WordsSheet.getRange(wordIndex, min, 1, max - min + 1)
    let values = range.getValues()
    values[0][COLNAMES.attempts + shift] += results.attempts || 0
    values[0][COLNAMES.guessed + shift] += results.guessed || 0
    values[0][COLNAMES.asked + shift] += 1
    range.setValues(values)

    return { values: values[0] }
}
