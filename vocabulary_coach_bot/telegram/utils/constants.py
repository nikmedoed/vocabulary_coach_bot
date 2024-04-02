from enum import Enum, auto


class StorageKeys(Enum):
    SHEET_URL = auto()
    PREVIOUS_MESSAGE_DATE = auto()
    PREVIOUS_REMINDER_ID = auto()
    TRAINING_FREQUENCY = auto()
    CURRENT_QUESTION_ID = auto()
    SEND_SHEET_REMIND = auto()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
