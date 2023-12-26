// Все генераторы должны уметь обрабатывать как запрос одного вопроса, так и нескольких

// Генератор вопросов с одним словом
function getWord(params = {}) {
  let count = (params.count && parseInt(params.count)) || 1

  const properties = PropertiesService.getDocumentProperties()
  var previously_asked = properties.getProperty('previously_asked')
  previously_asked = previously_asked ? JSON.parse(previously_asked) : []

  if (WordsSheet.getLastRow() < 2) {
    return { error: "База слов пустая" }
  }

  if (WordsSheet.getLastRow() < 2 + count) {
    return { error: "В базе слишком мало слов" }
  }

  var questions = getWordsForQuestions(count, previously_asked)

  // Обновить хранилище
  const totalWords = WordsSheet.getLastRow() - 1;
  const maxQueueSize = (totalWords * 2 / 3) - questions.length;
  const numberOfElementsToRemove = Math.max(previously_asked.length - maxQueueSize, 0);
  previously_asked = previously_asked.slice(numberOfElementsToRemove);

  properties.setProperty('previously_asked', JSON.stringify([...previously_asked, ...questions.map(w => w.id)]))

  return retrunFix(questions)
}


// Генератор вопроса с выбором одного правильного
function getWords(params = {}) {
  if (WordsSheet.getLastRow() < 8) {
    return { error: "Требуется не меньше 16 слов в базе" }
  }
  var words = getWord(params)
  if (!(words instanceof Array)) {
    words = [words]
  }
  var data = WordsSheet.getSheetValues(2, COLNAMES.word + 1, WordsSheet.getLastRow() - 1, 1)
    .map((el) => el[0])
  words = words.map(word => setWrongVariants(word, data))
  return retrunFix(words)
}


// Добавить неправильные варианты к вопросу, к примеру, с выбором
function setWrongVariants(word, data, count = 8) {
  var variants = new Set([word.row - 2])
  while (variants.size < count) {
    variants.add(Math.floor(Math.random() * data.length))
  }
  word.variants = shuffle(Array.from(variants).map(e => data[e]))
  return word
}
