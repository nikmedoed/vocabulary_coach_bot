from telegram.utils.texts_enum import EnumContent


class Commands(EnumContent):
    settings = "настройки уведомлений и интересов",
    start = "запустить бота (тренировку)",
    help = "список команд",
    privacy = "о хранении данных"


class General(EnumContent):
    bot_started = "Бот запустился или перезапустился"
    help = (
               "Данный бот помогает заучивать ответы на вопросы. В первую очередь он ориентирован на изучение иностранных слов.\n"
               "\n"
               "Для работы требуется:\n"
               "- скопировать <a href='https://docs.google.com/spreadsheets/d/1FvD3tg18_Gx9mD71T2cI6UiVrfnZ8ikgp0hAV7GpBeU/'>специальную табличку</a>\n"
               "- развернуть по <a href='https://github.com/nikmedoed/vocabulary_coach_bot/blob/main/docs/deploy_table.md'>инструкции</a>\n"
               "- привязать к своему аккаунту (отправить боту)\n"
               "- заполнить таблицу данными\n"
               "- запустить процесс изучения \n"
               "\n"
               "Комманды бота:\n"
               "{}\n"
               "\n"
               "Если бот работает некорректно, писать @nikmedoed"
           ).format('\n'.join([f'/{k.name} - {k}' for k in Commands])),
    privacy = ("Бот хранит все ответы на вопросы, которые влияют на его работу:\n"
               "<pre>- Ваш id\n"
               "- Ссылку на вашу таблицу (данные из этой таблицы)\n"
               "- Статистику по использованию</pre>\n"
               "\n"
               "Срок хранения не ограничен.\n"
               "Все доступные боту данные могут быть использованы в рамках статистических исследований с последующей "
               "публикацией."),
    forward_to_admin = "Не получилось обработать сообщение, переслал @nikmedoed"


class Start(EnumContent):
    start = ("Привет!\n\n"
             "Надеюсь, этот бот поможет тебе в изучении.\n"
             "Подробнее о работе бота: /help")


class Settings(EnumContent):
    frequency_no = "Не напоминать"
    frequency_message = ("Через сколько часов напоминать о тренировках?\n"
                         "(Изменить можно в настройках)")
    frequency_set = "Напоминать каждые {} ч неактивности"
    frequency_set_no = "Не буду напоминать о тренировках"

    welcome = ("Кнопка «закрыть» скроет клавиатуру совсем, "
               "но вы можете её снова вернуть с помощью команды /settings.\n\n"
               "Также вы можете скрыть клавиатуру средствами Telegram.")

    button_frequency = "Изменить частоту оповещения"
    button_sheet = "Изменить ссылку на таблицу"
    button_close = "Закрыть настройки"

    sheet_url_message = ("👉 Сейчас мне нужна ссылка на настроенную таблицу.\n\n"
                         "<a href='https://github.com/nikmedoed/vocabulary_coach_bot/blob/main/docs/deploy_table.md'>Инструкция, как получить ссылку</a>")
    sheet_url_message_cancel = "Для отмены команда: /cancel"
    sheet_url_incorrect = ("Сообщение должно содержать корректную ссылку в формате:\n"
                           "<pre>https://script.google.com/macros/s/.../exec</pre>\n\n"
                           "👉 Пришлите корректную ссылку")
    sheet_url_correct = "Отлично, ссылка принята."


class CommandsAdmin(EnumContent):
    pass
    # "pollscycle": "провести работу со всеми пользователями",
    # "stat": "статистика по ???",
    # "activities": "работа по активностям ???",
    # "nextstage": "Следующий шаг",

    # "sync_paids": "Подзгрузить оплаты"


class Admin(EnumContent):
    frequency_no = "Не напоминать"
    broadcast_message_confirm = "Разосласть всем это сообщение?"
    broadcast_message_confirm_no = "Рассылка отменена"
    broadcast_message_confirm_yes = "Рассылка начата"


class Trainings(EnumContent):
    select_message = ("<b>Выберите тип тренировки</b>\n\n"
                      "Через это сообщение можно переключить вид тренировки.\n\n"
                      "Чтобы вывести данное сообщение, отправьте команду /start (можно выбрать в меню)")

    training_type_the_answer = "Написать ответ"
    training_select_one = "Выбрать ответ"

    instruction_training_type_the_answer = "Напишите ответ в точности"
    instruction_training_select_one = "Выберите верный вариант"

    question = ("❓ <b>Вопрос:</b>\n"
                "{question}\n\n"
                "{hint}"
                "<i>{instruction}</i>")
    answer = ("❓ <b>Вопрос:</b>\n"
              "{question}\n\n"
              "👌 <b>Ответ:</b>\n"
              "{word}")
    hint = "🤙 <b>Подсказка:</b>\n{}\n\n"
    hint_no = "<i>🔩 Не указано</i>"

    start_message = ", поехали!!!"
    stop_message = ("<b>Сначала завершите текущую тренировку</b>\n\n"
                    "Для смены режима, изменения настроек и т.п., завершите текущую серию.")

    button_stop = "🛑 Завершить тренировку"
    button_next = "⏭ Сдаюсь, дальше"
    button_hint = "🤙 Показать подсказку"

    answer_score_100 = "Отлично!"
    answer_score_90 = "Почти"
    answer_score_65 = "Похоже"
    answer_score_0 = "Неверно"

    answer_select_one_none = "Этот вариант уже неактивен"

    remind_start = ("<b>Время прошло, пора тренироваться</b>\n"
                    "<i>Напоминаю, как вы просили</i>\n\n")
    remind_continue = ("<b>Напоминаю о тренировке</b>\n\n"
                       "В данный момент вы уже находитесь в режиме тренировки:\n"
                       "<i>{}</i>\n\n"
                       "Продолжайте, или завершите её")
    remind_read = "Ок, продолжаем"
    remind_pause = "⏸ Отложить на {}ч"
    remind_pause_ok = "Напомню через {}ч"



class Misc(EnumContent):
    eyes = "🧐 👀 👁 👁‍🗨 🙄".split()


class Text:
    general = General
    commands = Commands
    start = Start
    settings = Settings
    admin = Admin
    commands_admin = CommandsAdmin
    trainings = Trainings
    misc = Misc


if __name__ == "__main__":
    print(
        Text.commands.settings,
        Text.general.help,

        sep="\n====\n"

    )
