// TODO

// Механизм обновления, т.е. проверка и сохранение версий, а также пошаговое автоматическое безопасное обновление данных в таблице

// подбирать варианты схожие по длине по возможности в setWrongVariants

// Отдельная колонка для транскрипций

const SSheet = SpreadsheetApp.getActiveSpreadsheet()
const WordsSheet = SSheet.getSheetByName("Words")
const COLNAMES = getColNames({
  word: "Ответ",
  question: "Вопрос (пояснение)",
  hint: "Подсказка",
  asked: "Задано раз",
  attempts: "Попыток",
  guessed: "Угадано",
  access: "Последний раз задано",
  id: 'id'
})