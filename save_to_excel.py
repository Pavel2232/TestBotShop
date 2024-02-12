from openpyxl import Workbook


def save_emails_and_ids(emails_ids: list[tuple], filename: str):
    # Создаем новую книгу Excel
    wb = Workbook()
    # Выбираем активный лист (первый лист)
    ws = wb.active
    # Добавляем заголовки столбцов
    ws.append(['Telegram ID', 'Username'])
    # Добавляем данные почты и идентификатора Telegram в файл Excel
    for email, tg_id in emails_ids:
        ws.append([email, tg_id])
    # Сохраняем книгу в файл
    wb.save(filename)

