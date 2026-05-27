from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
import globals

db = Database("db-evos.db")


def inline_handler(update, context):
    query = update.callback_query
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)
    lang_id = db_user["lang_id"]

    if data_sp[0] == "category":
        # 1. ORQAGA QAYTISH LOGIKASI (back)
        if data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
            else:
                parent_id = None

            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = []
            row = []
            for i in range(len(categories)):
                row.append(
                    InlineKeyboardButton(
                        text=categories[i][f'name_{globals.LANGUAGE_CODE[lang_id]}'],
                        callback_data=f"category_{categories[i]['id']}"
                    )
                )

                if len(row) == 2 or (len(categories) % 2 == 1 and i == len(categories) - 1):
                    buttons.append(row)
                    row = []

            # Orqaga qaytganda yana orqaga qaytish tugmasini to'g'ri chiqarish
            if parent_id:
                clicked_btn = db.get_category_parent(parent_id)
                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="⬅️ Orqaga / Назад", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="⬅️ Orqaga / Назад", callback_data="category_back"
                    )])

            query.message.edit_text(
                text=globals.TEXT_CHOOSE_CATEGORY[lang_id],
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )

        # 2. TOIFA BOSILGANDAGI LOGIKA
        else:
            current_id = int(data_sp[1])
            categories = db.get_categories_by_parent(parent_id=current_id)

            # Agar ichida yana sub-toifalar bo'lsa
            if categories:
                buttons = []
                row = []
                for i in range(len(categories)):
                    row.append(
                        InlineKeyboardButton(
                            text=categories[i][f'name_{globals.LANGUAGE_CODE[lang_id]}'],
                            callback_data=f"category_{categories[i]['id']}"
                        )
                    )

                    if len(row) == 2 or (len(categories) % 2 == 1 and i == len(categories) - 1):
                        buttons.append(row)
                        row = []

                # TUGATILDI: "Orqaga" tugmasi 'for' siklidan TASHQARIGA olindi.
                # Endi u har bir versiya uchun takrorlanmaydi, faqat eng oxirida 1 marta qo'shiladi.
                clicked_btn = db.get_category_parent(current_id)
                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="⬅️ Orqaga / Назад", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="⬅️ Orqaga / Назад", callback_data="category_back"
                    )])

                query.message.edit_text(
                    text=globals.TEXT_CHOOSE_CATEGORY[lang_id],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )

            # Agar bu eng oxirgi mod bo'lsa (Faylni yuborish)
            else:
                mod_data = db.get_category_by_id(current_id)

                # Inline xabarni tozalaymiz
                query.message.delete()

                caption_uz = f"🎮 **RexCraft Mod Tizimi**\n\nSiz so'ragan *{mod_data['name_uz']}* fayli tayyor!\nUni yuklab olib `.minecraft/mods` papkasiga tashlang."
                caption_ru = f"🎮 **Система модов RexCraft**\n\nФайл *{mod_data['name_ru']}* готов!\nСкачайте и переместите в папку `.minecraft/mods`."
                caption_text = caption_uz if lang_id == 1 else caption_ru

                if mod_data and mod_data.get('file_id'):
                    context.bot.send_document(
                        chat_id=query.message.chat_id,
                        document=mod_data['file_id'],
                        caption=caption_text,
                        parse_mode="Markdown"
                    )
                else:
                    # Agar  fayl hali yuklanmagan bo'lsa
                    download_url = f"https://t.me/rexcraft_mod_fayllari/{current_id}"
                    mod_buttons = [
                        [InlineKeyboardButton(text="📥 Havola orqali yuklash", url=download_url)],
                        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="category_back")]
                    ]
                    context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=caption_text + "\n\n(Fayl hali botga yuklanmagan)",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=mod_buttons),
                        parse_mode="Markdown"
                    )