import logging
import openai
import vk_api
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, ConversationHandler, CallbackContext
import nltk
from vk_api.longpoll import VkLongPoll, VkEventType
import langchain

nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer


TELEGRAM_TOKEN = "6078973247:AAETtI7TSgUWDK9i9EMxmlE2KAEjA0bxuHc"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Я бот, который может общаться с тобой и отвечать на твои вопросы. Задай мне вопрос.')

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text('Просто задайте мне вопрос, и я постараюсь найти ответ.')


def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    return sentiment

def translate_text(text):
    lc = langchain()
    translated_text = lc.translate(text, target='en')
    return translated_text

def handle_message(update: Update, context: CallbackContext):
    query = update.message.text
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"{query}\n\nAsol:",
            temperature=1.5,
            max_tokens=500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        answer = response.choices[0].text.strip()
        update.message.reply_text(answer)
    except Exception as e:
        update.message.reply_text('Извините, я не смог найти ответ на ваш вопрос.')

def main():
    logging.basicConfig(level=logging.INFO)

    vk_session = vk_api.VkApi(token='vk1.a.6Mhs6g7eAImiH1RryJZDFUVlmQb7aaaTbVhxegFqCU3dQ3B1BQMWNs8nnp33t-og7AyjdPVJl8xJ5zL6BF3awGihE9MOFyerARYNkMGlxN0QWrpEVHcuH1il4qrXKux03At6RRl9PY8L38nY4YcEG1CcVip44HKpY7Dj6uBmNhGtaLFhNCr7nLX2xHeyMgD2nIDqFOlPvict74-SygadIw')
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            message_text = event.text

            # Здесь можно обработать сообщение, проанализировать его тональность и сформировать ответ
            sentiment = analyze_sentiment(message_text)

            response_text = "Привет! Я получил ваше сообщение: " + message_text + \
                            ". Тональность вашего сообщения: " + str(sentiment)

            vk.messages.send(
                user_id=user_id,
                message=response_text,
                random_id=0
            )


    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
