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

function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('🤖 Get link for bot')
    .addItem('Get Link', 'VocabularyCoachBot.showInstructions')
    .addToUi();
}

const VocabularyCoachBot = {
  showInstructions: showInstructions
}

function showInstructions() {
  var ui = SpreadsheetApp.getUi();
  var url = ScriptApp.getService().getUrl();

  if (url) {
    ui.alert('Send this link to the bot:\n\n' + url);
  } else {
    var htmlOutput = HtmlService.createHtmlOutput(
      'Link not available. Please follow the <a href="https://github.com/nikmedoed/vocabulary_coach_bot/blob/main/docs/deploy_table.md" target="_blank">instructions</a> for deployment.'
    ).setWidth(400).setHeight(150);
    ui.showModalDialog(htmlOutput, 'Deployment Instructions');
  }
}