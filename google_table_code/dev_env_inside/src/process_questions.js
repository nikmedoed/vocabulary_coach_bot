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
  var data = getDataColumnValues(COLNAMES.word)
  words = words.map(word => setWrongVariants(word, data))
  return retrunFix(words)
}


// Добавить неправильные варианты к вопросу, к примеру, с выбором
function setWrongVariants(word, data, count = 8) {
  const mainWordLength = word.word.length; 
  let lengthTolerance = Math.max(Math.ceil(mainWordLength * 0.33), 4)
  const dataLength = data.length;
  let attempts = 0;
  const maxAttempts = Math.min(50 * count, dataLength)

  var variants = new Set([word.word]);
  while (variants.size < count) {
    const candidate = data[Math.floor(Math.random() * data.length)];
    if (Math.abs(candidate.length - mainWordLength) <= lengthTolerance || Math.random() < (attempts / maxAttempts)) {
      variants.add(candidate);
    }
    attempts++
  }

  word.variants = shuffle(Array.from(variants));
  return word;
}