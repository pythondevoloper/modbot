from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from database import Database
from register import check
from messages import message_handler, admin_document_handler  # admin_document_handler qo'shildi
from inlines import inline_handler

ADMIN_ID = 8193831651
TOKEN = "8936396576:AAHsM1z1W8R--rQ0QJBWEeylurejhnDlW3E"

db = Database("db-evos.db")  # O'zingiz ishlatayotgan baza nomi


def start_handler(update, context):
    check(update, context)


def contact_handler(update, context):
    message = update.message.contact.phone_number
    user = update.message.from_user
    db.update_user_data(user.id, "phone_number", message)
    check(update, context)


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))

    # ADMIN uchun fayl yuklash xandleri (Filters.document faqat fayllarni ushlaydi)
    dispatcher.add_handler(MessageHandler(Filters.document, admin_document_handler))

    dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    dispatcher.add_handler(MessageHandler(Filters.contact, contact_handler))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()