from random import shuffle

from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from telegram.texts import Text


class Trainings(StatesGroup):
    training_type_the_answer = State()
    training_select_one = State()


class TrainingsCallbackData(CallbackData, prefix="trainings"):
    type: str


class TrainingActionCallbackData(CallbackData, prefix="training_action"):
    action: str


class TrainingSelectOneCallbackData(CallbackData, prefix="TSOb"):
    word_number: str


def training_button_stop():
    return types.InlineKeyboardButton(
        text=Text.trainings.button_stop.value,
        callback_data=TrainingActionCallbackData(action="stop").pack()
    )


def generate_question_buttons_default(hint=False):
    markup = []
    if not hint:
        markup.append(types.InlineKeyboardButton(
            text=Text.trainings.button_hint.value,
            callback_data=TrainingActionCallbackData(action="hint").pack()
        ))
    markup.extend([types.InlineKeyboardButton(
        text=Text.trainings.button_next.value,
        callback_data=TrainingActionCallbackData(action="next").pack()
    ), training_button_stop()])
    return markup


def generate_training_select_one_buttons(question: dict):
    variants = question['variants']
    return [types.InlineKeyboardButton(
        text=f"❔ {word}",
        callback_data=TrainingSelectOneCallbackData(word_number=str(n)).pack()
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
    inline_keyboard = []
    row = []
    for b in special_buttons:
        if len(b.text) < 21:
            row.append(b)
        else:
            if row:
                inline_keyboard.append(row)
                row = []
            inline_keyboard.append([b])
        if len(row) > 1:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)
    for b in generate_question_buttons_default(hint):
        inline_keyboard.append([b])
    markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return {'text': text, 'reply_markup': markup}


async def training_select_message_generator(state: FSMContext | None = None):
    markup = training_select_keyboard(state and (await state.get_state()))
    return Text.trainings.select_message, markup


def training_select_keyboard(state: str):
    what = "training_"
    state = state and state.split(":")[-1] or ""
    buttons = [types.InlineKeyboardButton(
        text=f"{'✅ ' if state == butt.name else ''}{butt.value}",
        callback_data=TrainingsCallbackData(type=butt.name).pack()
    ) for butt in Text.trainings if butt.name.startswith(what)]
    inline_keyboard = []
    for i in range(0, len(buttons), 2):
        inline_keyboard.append(buttons[i:i + 2])
    return types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
