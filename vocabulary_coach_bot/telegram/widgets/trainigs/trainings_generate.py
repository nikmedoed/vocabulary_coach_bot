from random import shuffle

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.callback_data import CallbackData

from telegram.texts import Text


class Trainings(StatesGroup):
    training_type_the_answer = State()
    training_select_one = State()


trainings_cb = CallbackData('trainings', 'type')
training_action_button = CallbackData('training_action', 'action')
training_select_one_button = CallbackData('TSOb', 'word_number')


def training_button_stop():
    return types.InlineKeyboardButton(
        Text.trainings.button_stop.value,
        callback_data=training_action_button.new(action="stop")
    )


def generate_question_buttons_default(hint=False):
    markup = []
    if not hint:
        markup.append(types.InlineKeyboardButton(
            Text.trainings.button_hint.value,
            callback_data=training_action_button.new(action="hint")
        ))
    markup.extend([types.InlineKeyboardButton(
        Text.trainings.button_next.value,
        callback_data=training_action_button.new(action="next")
    ), training_button_stop()])
    return markup


def generate_training_select_one_buttons(question: dict):
    variants = question['variants']
    return [types.InlineKeyboardButton(
        f"❔ {word}",
        callback_data=training_select_one_button.new(word_number=n)
    ) for n, word in enumerate(variants)]


def generate_question_message(question: dict, train_type: str, hint=False):
    text = Text.trainings.question.value.format(
        question=question['question'],
        hint=Text.trainings.hint.value.format(
            question['hint'] + "\n" if question['hint'] else Text.trainings.hint_no.value
        ) if hint else "",
        instruction=Text.trainings[f"instruction_{train_type}"]
    )
    try:
        special_buttons = globals()[f"generate_{train_type}_buttons"](question)
    except (AttributeError, KeyError) as e:
        special_buttons = []
    # TODO проверить как лучше по 1, по 2,  или как ниже. А может вообще считать общую длину слов (т.е. и по 3)
    markup = types.InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    row = []
    for b in special_buttons:
        if len(b.text) < 21:
            row.append(b)
        else:
            markup.row(b)
        if len(row) > 1:
            markup.row(*row)
            row = []
    markup.row(*row)
    for b in generate_question_buttons_default(hint):
        markup.row(b)
    return {'text': text, 'reply_markup': markup}


async def training_select_message_generator(state: FSMContext = ""):
    markup = training_select_keyboard(state and (await state.get_state()))
    return Text.trainings.select_message, markup


def training_select_keyboard(state: str):
    what = "training_"
    state = state and state.split(":")[-1] or ""
    markup = types.InlineKeyboardMarkup(row_width=2).add(*[types.InlineKeyboardButton(
        f"{'✅ ' if state == butt.name else ''}{butt.value}",
        callback_data=trainings_cb.new(type=butt.name)
    ) for butt in Text.trainings if butt.name.startswith(what)])
    return markup
