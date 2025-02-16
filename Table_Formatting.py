import openpyxl
import csv
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

'''Чтение csv-файлов и конвертация в excel-формат'''
# wb = openpyxl.Workbook()
# ws = wb.active
#
# with open('Aviasales_Flights.csv', encoding='utf8') as f:
#     reader = csv.reader(f, delimiter=',')
#     for row in reader:
#         ws.append(row)
#
# wb.save('Aviasales_Flights.xlsx')

'''
1. Создаём список с названиями эксель-файлов, подлежащих форматированию.
2. Проходимся циклом по этим файлам. 
3. Создаём автофильтры для каждой колонки.
4. Настраиваем ширину, чтобы заголовки колонок и значения ячеек отображались полностью.
5. Создаём объект класса Border для создания границ ячеек.
6. Выделяем первую строку (заголовки) полужирным шрифтом.
7. Выравниваем значения ячеек по центру.
8. У ячеек в колонках "Минимальная цена", "Время вылета/прилёта" инициализируем переменные cell.fill 
и присваиваем им значения кодировок соответствующих цветов; цены дополнительно выделяем жирным шрифтом.'''

docs = ['Aviasales_Flights.xlsx', 'TuTu_Flights.xlsx']
for doc in docs:
    avia_book = openpyxl.load_workbook(doc)
    sheet = avia_book['Sheet']
    sheet.auto_filter.ref = 'A1:G999'
    sheet.column_dimensions['A'].width = 20
    sheet.column_dimensions['B'].width = 20
    sheet.column_dimensions['C'].width = 20
    sheet.column_dimensions['D'].width = 20
    sheet.column_dimensions['E'].width = 20
    sheet.column_dimensions['F'].width = 90
    sheet.column_dimensions['G'].width = 30

    thin_border = Border(
        left=Side(border_style="thin"),
        right=Side(border_style="thin"),
        top=Side(border_style="thin"),
        bottom=Side(border_style="thin")
    )
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.border = thin_border

    for column in sheet.columns:
        for cell in column:
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border

    light_orange_fill = PatternFill(start_color='E3CFC3', end_color='E3CFC3', fill_type='solid')

    for cell in sheet['G']:
        cell.fill = light_orange_fill
        cell.font = Font(bold=True)
        cell.border = thin_border

    light_green_fill = PatternFill(start_color='CFE4B7', end_color='CFE4B7', fill_type='solid')

    for cell in sheet['D']:
        cell.fill = light_green_fill
        cell.border = thin_border

    for cell in sheet['E']:
        cell.fill = light_green_fill
        cell.border = thin_border

    avia_book.save(doc)
