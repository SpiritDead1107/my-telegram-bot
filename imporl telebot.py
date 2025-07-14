import os
import telebot
from telebot import types
from datetime import datetime

ADMIN_ID = 426269597  # <-- замени на свой user_id

import os
bot = telebot.TeleBot(os.environ['7834545929:AAFGIMWSTf2RtXIBnz3BTMElpBzzxOpMD4c'])

CATEGORIES = ['🍔 Еда', '🚗 Транспорт', '🎉 Развлечения', '🏠 Жильё', '📦 Другое']

# Папка для хранения данных
DATA_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'Бот', 'bot_data')
os.makedirs(DATA_DIR, exist_ok=True)

# --- Функции для работы с файлами пользователя ---
def get_balance_file(user_id):
    return os.path.join(DATA_DIR, f"balance_{user_id}.txt")

def get_history_file(user_id):
    return os.path.join(DATA_DIR, f"history_{user_id}.txt")

def read_balance(user_id):
    filename = get_balance_file(user_id)
    if not os.path.exists(filename):
        return 0.0
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return float(f.read())
        except:
            return 0.0

def write_balance(user_id, balance):
    filename = get_balance_file(user_id)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(balance))

def add_history(user_id, op_type, amount, category='-', comment=''):
    filename = get_history_file(user_id)
    with open(filename, 'a', encoding='utf-8') as f:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        f.write(f"{now};{op_type};{amount};{category};{comment}\n")

# --- Быстрые суммы ---
def quick_amount_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in range(100, 5100, 400):
        row = [str(j) for j in range(i, i+400, 100) if j <= 5000]
        markup.add(*row)
    markup.add("Ввести вручную")
    return markup

# --- Главное меню ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('➕ Добавить доход', '➖ Добавить расход')
    markup.add('💰 Баланс', '📋 История')
    markup.add('📅 История за период')
    markup.add('ℹ️ Помощь', '⚙️ Админ-хелп')
    return markup

# --- Обработчик кнопки помощи ---
HELP_TEXT = (
    "<b>Справка по боту:</b>\n\n"
    "• <b>➕ Добавить доход</b> — добавить доход с быстрым выбором суммы и комментарием.\n"
    "• <b>➖ Добавить расход</b> — добавить расход с выбором категории, суммы и комментарием.\n"
    "• <b>💰 Баланс</b> — показать текущий баланс.\n"
    "• <b>📋 История</b> — последние 10 операций.\n"
    "• <b>📅 За сегодня</b> — операции за сегодня.\n"
    "• <b>🗓 За месяц</b> — операции за месяц.\n"
    "• <b>📊 Годовая статистика</b> — доходы и расходы по месяцам.\n"
    "• <b>📅 Сравнить месяцы</b> — сравнение выбранных месяцев.\n"
    "• <b>🗓 Сравнить года</b> — сравнение по годам.\n\n"
    "<b>Админ-команды:</b> доступны только администратору через ⚙️ Админ-хелп."
)

@bot.message_handler(func=lambda m: m.text == 'ℹ️ Помощь')
def help_button(message):
    bot.send_message(message.chat.id, HELP_TEXT, parse_mode='HTML')

# --- Админ-хелп ---
ADMIN_HELP_TEXT = (
    "<b>Админ-команды:</b>\n\n"
    "🔴 <b>Сброс всех данных всех пользователей</b>\n"
    "<code>/reset_all_data</code>\n"
    "Удаляет все балансы и истории всех пользователей. Только для администратора.\n\n"
    "🟠 <b>Сброс данных конкретного пользователя</b>\n"
    "<code>/reset_user &lt;user_id&gt;</code>\n"
    "Удаляет только баланс и историю пользователя с указанным user_id.\n"
    "Пример: <code>/reset_user 123456789</code>\n\n"
    "user_id можно узнать через @userinfobot."
)

@bot.message_handler(commands=['adminhelp'])
def adminhelp_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ У вас нет доступа к админ-командам.", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, ADMIN_HELP_TEXT, parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '⚙️ Админ-хелп')
def adminhelp_button(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ У вас нет доступа к админ-командам.", parse_mode='HTML')
        return
    bot.send_message(message.chat.id, ADMIN_HELP_TEXT, parse_mode='HTML')

@bot.message_handler(commands=['reset_all_data'])
def reset_all_data(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ У вас нет прав для выполнения этой команды.")
        return
    count = 0
    for filename in os.listdir(DATA_DIR):
        if (filename.startswith('balance_') or filename.startswith('history_')) and filename.endswith('.txt'):
            os.remove(os.path.join(DATA_DIR, filename))
            count += 1
    bot.send_message(message.chat.id, f"✅ Все балансы и истории пользователей удалены! ({count} файлов)")

@bot.message_handler(commands=['reset_user'])
def reset_user(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ У вас нет прав для выполнения этой команды.")
        return
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Используйте: /reset_user <user_id>")
            return
        user_id = int(parts[1])
        files = [os.path.join(DATA_DIR, f"balance_{user_id}.txt"), os.path.join(DATA_DIR, f"history_{user_id}.txt")]
        deleted = 0
        for filename in files:
            if os.path.exists(filename):
                os.remove(filename)
                deleted += 1
        if deleted:
            bot.send_message(message.chat.id, f"✅ Баланс и история пользователя {user_id} удалены!")
        else:
            bot.send_message(message.chat.id, f"Нет данных для пользователя {user_id}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['start', 'menu'])
def start(message):
    text = (
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Я — твой личный бот для учёта финансов.\n"
        "Выбери действие из меню ниже 👇"
    )
    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu(),
        parse_mode='HTML'
    )

# --- ДОХОД ---
@bot.message_handler(func=lambda m: m.text == '➕ Добавить доход')
def income_command(message):
    msg = bot.send_message(
        message.chat.id,
        '<b>Введите сумму дохода:</b>',
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_income_amount)

def process_income_amount(message):
    user_id = message.from_user.id
    try:
        amount = float(message.text.replace(',', '.'))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Без комментария')
        msg = bot.send_message(message.chat.id, '<b>Добавьте комментарий к доходу или нажмите "Без комментария":</b>', reply_markup=markup, parse_mode='HTML')
        bot.register_next_step_handler(msg, process_income_comment, amount)
    except ValueError:
        msg = bot.send_message(message.chat.id, '⚠️ <b>Пожалуйста, введите число.</b>', reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        bot.register_next_step_handler(msg, process_income_amount)

def process_income_comment(message, amount):
    user_id = message.from_user.id
    comment = "" if message.text == "Без комментария" else message.text
    balance = read_balance(user_id) + amount
    write_balance(user_id, balance)
    add_history(user_id, 'Доход', amount, '-', comment)
    bot.send_message(
        message.chat.id,
        f"✅ <b>Доход {amount:.2f}₽ добавлен!</b>\n💬 <i>{comment or 'Без комментария'}</i>\n\n💰 <b>Текущий баланс:</b> <code>{balance:.2f}₽</code>",
        reply_markup=main_menu(),
        parse_mode='HTML'
    )

# --- РАСХОД ---
@bot.message_handler(func=lambda m: m.text == '➖ Добавить расход')
def expense_command(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for cat in CATEGORIES:
        markup.add(cat)
    msg = bot.send_message(message.chat.id, '<b>Выберите категорию расхода:</b>', reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(msg, process_expense_category)

def process_expense_category(message):
    user_id = message.from_user.id
    category = message.text
    if category not in CATEGORIES:
        bot.send_message(message.chat.id, '⚠️ <b>Пожалуйста, выберите категорию из списка.</b>', reply_markup=main_menu(), parse_mode='HTML')
        return
    msg = bot.send_message(
        message.chat.id,
        f'<b>Введите сумму расхода для категории {category}:</b>',
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode='HTML'
    )
    bot.register_next_step_handler(msg, process_expense_amount, category)

def process_expense_amount(message, category):
    user_id = message.from_user.id
    try:
        amount = float(message.text.replace(',', '.'))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add('Без комментария')
        msg = bot.send_message(message.chat.id, '<b>Добавьте комментарий к расходу или нажмите "Без комментария":</b>', reply_markup=markup, parse_mode='HTML')
        bot.register_next_step_handler(msg, process_expense_comment, amount, category)
    except ValueError:
        msg = bot.send_message(message.chat.id, '⚠️ <b>Пожалуйста, введите число.</b>', reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')
        bot.register_next_step_handler(msg, process_expense_amount, category)

def process_expense_comment(message, amount, category):
    user_id = message.from_user.id
    comment = "" if message.text == "Без комментария" else message.text
    balance = read_balance(user_id) - amount
    write_balance(user_id, balance)
    add_history(user_id, 'Расход', amount, category, comment)
    bot.send_message(
        message.chat.id,
        f"✅ <b>Расход {amount:.2f}₽ в категории '{category}' добавлен!</b>\n💬 <i>{comment or 'Без комментария'}</i>\n\n💰 <b>Текущий баланс:</b> <code>{balance:.2f}₽</code>",
        reply_markup=main_menu(),
        parse_mode='HTML'
    )

# --- ОСТАЛЬНЫЕ ФУНКЦИИ (баланс, история, статистика и т.д.) ---
# (оставить без изменений, только в истории добавить отображение комментария)

@bot.message_handler(func=lambda m: m.text == '💰 Баланс')
def stats_command(message):
    user_id = message.from_user.id
    balance = read_balance(user_id)
    bot.send_message(
        message.chat.id,
        f"💰 <b>Текущий баланс:</b> <code>{balance:.2f}₽</code>",
        reply_markup=main_menu(),
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda m: m.text == '📋 История')
def history_command(message):
    user_id = message.from_user.id
    filename = get_history_file(user_id)
    if not os.path.exists(filename):
        bot.send_message(message.chat.id, "📋 <b>История пуста.</b>", reply_markup=main_menu(), parse_mode='HTML')
        return
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-10:]  # последние 10 операций
    if not lines:
        bot.send_message(message.chat.id, "📋 <b>История пуста.</b>", reply_markup=main_menu(), parse_mode='HTML')
        return
    text = "📋 <b>Последние операции:</b>\n\n"
    for line in lines:
        try:
            date, op_type, amount, category, comment = line.strip().split(';')
            op_emoji = '➕' if op_type == 'Доход' else '➖'
            cat = category if category != '-' else ''
            comm = f"\n💬 <i>{comment}</i>" if comment else ''
            text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {date}\n\n"
        except Exception:
            continue
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

# --- История за период ---
@bot.message_handler(func=lambda m: m.text == '📅 История за период')
def period_history_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('Сегодня', 'Неделя', 'Месяц')
    markup.add('Сравнить месяцы')
    markup.add('⬅️ В меню')
    msg = bot.send_message(message.chat.id, '<b>Выберите период или действие:</b>', reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(msg, process_period_choice)

def process_period_choice(message):
    user_id = message.from_user.id
    period = message.text
    if period == '⬅️ В меню':
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=main_menu())
        return
    if period == 'Сравнить месяцы':
        compare_months_command(message)
        return
    filename = get_history_file(user_id)
    if not os.path.exists(filename):
        bot.send_message(message.chat.id, '📋 <b>История пуста.</b>', reply_markup=main_menu(), parse_mode='HTML')
        return
    now = datetime.now()
    lines = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                date_str, op_type, amount, category, comment = line.strip().split(';')
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                if period == 'Сегодня' and date.date() == now.date():
                    lines.append(line)
                elif period == 'Неделя' and (now.date() - date.date()).days < 7:
                    lines.append(line)
                elif period == 'Месяц' and date.year == now.year and date.month == now.month:
                    lines.append(line)
            except Exception:
                continue
    if not lines:
        bot.send_message(message.chat.id, f'📋 <b>В выбранный период операций не было.</b>', reply_markup=main_menu(), parse_mode='HTML')
        return
    period_text = {'Сегодня': 'за сегодня', 'Неделя': 'за неделю', 'Месяц': 'за месяц'}
    text = f"📅 <b>Операции {period_text.get(period, '')}:</b>\n\n"
    for line in lines:
        try:
            date, op_type, amount, category, comment = line.strip().split(';')
            op_emoji = '➕' if op_type == 'Доход' else '➖'
            cat = category if category != '-' else ''
            comm = f"\n💬 <i>{comment}</i>" if comment else ''
            time_str = date if period != 'Сегодня' else date[11:]
            text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {time_str}\n\n"
        except Exception:
            continue
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '📅 Сравнить месяцы')
def compare_months_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    months = [datetime.now().strftime('%Y-%m')]
    for i in range(1, 12):
        months.append(datetime(datetime.now().year, datetime.now().month - i, 1).strftime('%Y-%m'))
    markup.add(*months)
    markup.add('⬅️ В меню')
    msg = bot.send_message(message.chat.id, '<b>Выберите месяц для сравнения:</b>', reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(msg, process_compare_months)

def process_compare_months(message):
    user_id = message.from_user.id
    if message.text == '⬅️ В меню':
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=main_menu())
        return

    try:
        selected_month = datetime.strptime(message.text, '%Y-%m')
        current_month = datetime.now().strftime('%Y-%m')
        current_month_obj = datetime.strptime(current_month, '%Y-%m')

        if selected_month > current_month_obj:
            bot.send_message(message.chat.id, "⚠️ <b>Выбранный месяц не может быть в будущем.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        filename = get_history_file(user_id)
        if not os.path.exists(filename):
            bot.send_message(message.chat.id, "📋 <b>История пуста.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        current_month_lines = []
        selected_month_lines = []

        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    date_str, op_type, amount, category, comment = line.strip().split(';')
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                    if date.year == selected_month.year and date.month == selected_month.month:
                        selected_month_lines.append(line)
                    elif date.year == current_month_obj.year and date.month == current_month_obj.month:
                        current_month_lines.append(line)
                except Exception:
                    continue

        if not current_month_lines and not selected_month_lines:
            bot.send_message(message.chat.id, "📋 <b>В выбранные месяцы операций не было.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        text = f"<b>Сравнение за {selected_month.strftime('%Y-%m')} и {current_month_obj.strftime('%Y-%m')}:</b>\n\n"
        if current_month_lines:
            text += "<b>Текущий месяц:</b>\n"
            for line in current_month_lines:
                try:
                    date, op_type, amount, category, comment = line.strip().split(';')
                    op_emoji = '➕' if op_type == 'Доход' else '➖'
                    cat = category if category != '-' else ''
                    comm = f"\n💬 <i>{comment}</i>" if comment else ''
                    text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {date[11:]}\n\n"
                except Exception:
                    continue
            text += "\n"

        if selected_month_lines:
            text += f"<b>Выбранный месяц ({selected_month.strftime('%Y-%m')}):</b>\n"
            for line in selected_month_lines:
                try:
                    date, op_type, amount, category, comment = line.strip().split(';')
                    op_emoji = '➕' if op_type == 'Доход' else '➖'
                    cat = category if category != '-' else ''
                    comm = f"\n💬 <i>{comment}</i>" if comment else ''
                    text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {date[11:]}\n\n"
                except Exception:
                    continue

        bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

    except ValueError:
        bot.send_message(message.chat.id, "⚠️ <b>Пожалуйста, выберите месяц из списка.</b>", reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == '🗓 Сравнить года')
def compare_years_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    years = [datetime.now().year]
    for i in range(1, 5): # Сравнить с последними 5 годами
        years.append(datetime.now().year - i)
    markup.add(*years)
    markup.add('⬅️ В меню')
    msg = bot.send_message(message.chat.id, '<b>Выберите год для сравнения:</b>', reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(msg, process_compare_years)

def process_compare_years(message):
    user_id = message.from_user.id
    if message.text == '⬅️ В меню':
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=main_menu())
        return

    try:
        selected_year = int(message.text)
        current_year = datetime.now().year

        if selected_year > current_year:
            bot.send_message(message.chat.id, "⚠️ <b>Выбранный год не может быть в будущем.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        filename = get_history_file(user_id)
        if not os.path.exists(filename):
            bot.send_message(message.chat.id, "📋 <b>История пуста.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        current_year_lines = []
        selected_year_lines = []

        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    date_str, op_type, amount, category, comment = line.strip().split(';')
                    date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
                    if date.year == selected_year:
                        selected_year_lines.append(line)
                    elif date.year == current_year:
                        current_year_lines.append(line)
                except Exception:
                    continue

        if not current_year_lines and not selected_year_lines:
            bot.send_message(message.chat.id, "📋 <b>В выбранные годы операций не было.</b>", reply_markup=main_menu(), parse_mode='HTML')
            return

        text = f"<b>Сравнение за {selected_year} и {current_year}:</b>\n\n"
        if current_year_lines:
            text += "<b>Текущий год:</b>\n"
            for line in current_year_lines:
                try:
                    date, op_type, amount, category, comment = line.strip().split(';')
                    op_emoji = '➕' if op_type == 'Доход' else '➖'
                    cat = category if category != '-' else ''
                    comm = f"\n💬 <i>{comment}</i>" if comment else ''
                    text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {date[11:]}\n\n"
                except Exception:
                    continue
            text += "\n"

        if selected_year_lines:
            text += f"<b>Выбранный год ({selected_year}):</b>\n"
            for line in selected_year_lines:
                try:
                    date, op_type, amount, category, comment = line.strip().split(';')
                    op_emoji = '➕' if op_type == 'Доход' else '➖'
                    cat = category if category != '-' else ''
                    comm = f"\n💬 <i>{comment}</i>" if comment else ''
                    text += f"{op_emoji} <b>{op_type}</b> | <i>{cat}</i> | <code>{float(amount):.2f}₽</code>{comm}\n🕒 {date[11:]}\n\n"
                except Exception:
                    continue

        bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode='HTML')

    except ValueError:
        bot.send_message(message.chat.id, "⚠️ <b>Пожалуйста, выберите год из списка.</b>", reply_markup=main_menu(), parse_mode='HTML')

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(message.chat.id, "ℹ️ <b>Пожалуйста, выберите действие из меню:</b>", reply_markup=main_menu(), parse_mode='HTML')

bot.infinity_polling()