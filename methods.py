from telegram import KeyboardButton, ReplyKeyboardMarkup
import globals


def send_main_menu(context, chat_id, lang_id, message_id=None):
    buttons = [
        [KeyboardButton(text=globals.BTN_MODS[lang_id])],
        [KeyboardButton(text=globals.BTN_CHANNEL[lang_id]), KeyboardButton(text=globals.BTN_SETTINGS[lang_id])]
    ]

    context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_MAIN_MENU[lang_id],
        reply_markup=ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )
    )