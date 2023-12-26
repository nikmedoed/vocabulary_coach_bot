from telegram.utils.google_ask import google_ask


class SpreadSheetConnector:

    @staticmethod
    async def check_version(sheet_url):
        return (await google_ask({
            "method": "check_version"
        }, sheet_url))['version']

    @staticmethod
    async def training_type_the_answer(sheet_url, count=1):
        return await google_ask({
            "method": "get_word",
            "data": {
                "count": count
            }
        }, sheet_url)

    @staticmethod
    async def training_select_one(sheet_url, count=1):
        return await google_ask({
            "method": "get_words",
            "data": {
                "count": count
            }
        }, sheet_url)

    @staticmethod
    async def set_result(sheet_url, word, attempts=1, guessed=1):
        if type(word) == dict:
            data = word
        else:
            data = {
                "word": word,
                "attempts": attempts,
                "guessed": guessed
            }
        return await google_ask({
            "method": "set_result",
            "data": data
        }, sheet_url)
