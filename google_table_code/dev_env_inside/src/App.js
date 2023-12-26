const SSheet = SpreadsheetApp.getActiveSpreadsheet()
const Sheet = SSheet.getSheetByName("Words")
const COLNAMES = getColNames()

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

}

function checkVersion() {
  return { version: "1.1" }
}

const METHODS = {
  get_word: getWord,
  get_words: getWords,
  set_result: setResults,
  check_version: checkVersion
}

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
}

function getWordsForQuestions(count, previously_asked) {
  var selectedWords = []

  var data = Sheet.getSheetValues(2, 1, Sheet.getLastRow() - 1, Sheet.getLastColumn())
    .map((el, ind) => [...el, ind + 2])
  var paSet = new Set(previously_asked)
  var notAsked = data.filter(el => !paSet.has(el[COLNAMES.id]))

  var redline = new Date()
  redline.setHours(redline.getHours() - 1)
  var fresh = notAsked.filter(el => !el[COLNAMES.access] || el[COLNAMES.access] < redline)

  if (fresh.length < count) {
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
  } else {
    selectedWords = get_random_elements(fresh, count)
  }

  return selectedWords
}

function packWordRow(wordRow) {
  const selected_index = wordRow[wordRow.length - 1]
  var word = { row: selected_index }

  for (var key in COLNAMES) {
    word[key] = wordRow[COLNAMES[key]]
  }

  if (!wordRow[COLNAMES.id]) {
    let row = Sheet.getRange(selected_index, 1, 1, Sheet.getLastColumn())
    wordRow = row.getValues()[0]
    wordRow[COLNAMES.id] = Math.max(...getDataColumnValues(COLNAMES.id)) + 1
    wordRow[COLNAMES.access] = new Date()
    row.setValues([wordRow])
  }
  else {
    Sheet.getRange(selected_index, COLNAMES.access + 1).setValue(new Date())
  }
  return word
}

function retrunFix(arr) {
  return arr.length == 1 ? arr[0] : arr
}


function getWord(params = {}) {
  let count = (params.count && parseInt(params.count)) || 1

  const properties = PropertiesService.getDocumentProperties()
  var previously_asked = properties.getProperty('previously_asked')
  previously_asked = previously_asked ? JSON.parse(previously_asked) : []

  if (Sheet.getLastRow() < 2) {
    return { error: "База слов пустая" }
  }

  if (Sheet.getLastRow() < 2 + count) {
    return { error: "В базе слишком мало слов" }
  }

  var selectedWords = getWordsForQuestions(count, previously_asked)
  var questions = selectedWords.map(w => packWordRow(w))

  // Обновить хранилище
  const totalWords = Sheet.getLastRow() - 1;
  const maxQueueSize = (totalWords * 2 / 3) - questions.length;
  const numberOfElementsToRemove = Math.max(previously_asked.length - maxQueueSize, 0);
  previously_asked = previously_asked.slice(numberOfElementsToRemove);

  properties.setProperty('previously_asked', JSON.stringify([...previously_asked, ...questions.map(w => w.id)]))
  
  return retrunFix(questions)
}


function shuffle(array) {
  for (var i = array.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1))
    let t = array[i]; array[i] = array[j]; array[j] = t
  }
  return array
}

function setWrongVariants(word, data, count = 8) {
  var variants = new Set([word.row - 2])
  while (variants.size < count) {
    variants.add(Math.floor(Math.random() * data.length))
  }
  word.variants = shuffle(Array.from(variants).map(e => data[e]))
  return word
}

function getWords(params = {}) {
  if (Sheet.getLastRow() < 8) {
    return { error: "Требуется не меньше 16 слов в базе" }
  }
  var words = getWord(params)
  if (!(words instanceof Array)) {
    words = [words]
  }
  var data = Sheet.getSheetValues(2, COLNAMES.word + 1, Sheet.getLastRow() - 1, 1)
    .map((el) => el[0])
  words = words.map(word => setWrongVariants(word, data))
  return retrunFix(words)
}

function getDataColumnValues(id) {
  return Sheet.getSheetValues(2, id + 1, Sheet.getLastRow() - 1, 1).map((el) => el[0])
}


function setResults(results) {
  let wordIndex = -1

  if (results.id) {
    results.id = parseInt(results.id)
    wordIndex = getDataColumnValues(COLNAMES.id).indexOf(results.id)
  }
  if (wordIndex == -1 || Sheet.getSheetValues(2 + wordIndex, COLNAMES.word + 1, 1, 1)[0] != results.word) {
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

  var range = Sheet.getRange(wordIndex, min, 1, max - min + 1)
  let values = range.getValues()
  values[0][COLNAMES.attempts + shift] += results.attempts || 0
  values[0][COLNAMES.guessed + shift] += results.guessed || 0
  values[0][COLNAMES.asked + shift] += 1
  range.setValues(values)

  return { values: values[0] }
}


