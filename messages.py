from register import check, check_data_decorator
from database import Database
import globals
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import methods

db = Database("db-evos.db")
ADMIN_ID = 8193831651  # Sizning ID raqamingiz


def admin_document_handler(update, context):
    user_id = update.message.from_user.id
    if user_id == ADMIN_ID:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name

        context.user_data["waiting_file_id"] = file_id
        context.user_data["state"] = 99  # Admin fayl yuklash holati

        update.message.reply_text(
            f"📥 **Mod fayli qabul qilindi:** `{file_name}`\n\n"
            f"Endi ushbu mod qaysi toifaga tegishli ekanligini bilishim uchun "
            f"toifaning **ID raqamini** menga yozib yuboring!"
        )


@check_data_decorator
def message_handler(update, context):
    message = update.message.text
    user = update.message.from_user
    state = context.user_data.get("state", 0)
    db_user = db.get_user_by_chat_id(user.id)

    if state == 0:
        check(update, context)

    elif state == 1:
        if not db_user["lang_id"]:
            if message == globals.BTN_LANG_UZ:
                db.update_user_data(user.id, "lang_id", 1)
                check(update, context)
            elif message == globals.BTN_LANG_RU:
                db.update_user_data(user.id, "lang_id", 2)
                check(update, context)
            else:
                update.message.reply_text(text=globals.TEXT_LANG_WARNING)
        elif not db_user["first_name"]:
            db.update_user_data(user.id, "first_name", message)
            check(update, context)
        elif not db_user["last_name"]:
            db.update_user_data(user.id, "last_name", message)
            check(update, context)

    # Admin toifa ID raqamini yuborganida ishlaydigan qism
    elif state == 99 and user.id == ADMIN_ID:
        if message.isdigit():
            category_id = int(message)
            category = db.get_category_by_id(category_id)

            if category:
                file_id = context.user_data.get("waiting_file_id")
                db.update_category_file(category_id, file_id)

                update.message.reply_text(
                    f"✅ Muvaffaqiyatli saqlandi!\nMod: *{category['name_uz']}* toifasiga biriktirildi.",
                    parse_mode="Markdown"
                )
                context.user_data["state"] = 2
                methods.send_main_menu(context, user.id, db_user['lang_id'])
            else:
                update.message.reply_text("❌ Bunday ID raqamli toifa bazada topilmadi. Qaytadan yozing:")
        else:
            update.message.reply_text("⚠ Iltimos, faqat toifaning ID raqamini yozib yuboring:")

    # 🏠 ASOSIY MENYU HOLATI (Bu yer tartibga solindi)
    elif state == 2:
        # 1-shart: Agar foydalanuvchi "🎮 Mods" tugmasini bossa
        if message == globals.BTN_MODS[db_user['lang_id']]:
            categories = db.get_categories_by_parent(parent_id=None)

            if categories:
                buttons = []
                row = []
                for i in range(len(categories)):
                    row.append(
                        InlineKeyboardButton(
                            text=categories[i][f"name_{globals.LANGUAGE_CODE[db_user['lang_id']]}"],
                            callback_data=f"category_{categories[i]['id']}"
                        )
                    )
                    if len(row) == 2 or (len(categories) % 2 == 1 and i == len(categories) - 1):
                        buttons.append(row)
                        row = []

                update.message.reply_text(
                    text=globals.TEXT_CHOOSE_CATEGORY[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )
            else:
                update.message.reply_text("❌ Hozircha bazada hech qanday mod toifasi yo'q!")

        # 2-shart: Agar foydalanuvchi "🎬 Kanal haqida" tugmasini bossa (ixtiyoriy foydalanish uchun)
        elif message == "🎬 Kanal haqida" or message == "🎬 О канале":
            opisaniya_text = (
                "Salom barchaga! RexCraft kanaliga xush kelibsiz! 🚀\n\n"
                "Siz Minecraft-ni zerikarli vanila holatidan charchadingizmi? "
                "O'yiningizni butunlay o'zgartirib yuboradigan eng daxshatli va "
                "eng qiziqarli modlarni shu yerdan yuklab olishingiz mumkin! 🔥"
            )
            update.message.reply_text(text=opisaniya_text)

        # 3-shart: Agar menyudan tashqari boshqa matn yozilsa
        else:
            update.message.reply_text("Iltimos, menyudagi tugmalardan foydalaning! 👇")