# crm_integration/views.py
from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .forms import DealForm
import datetime
# Декоратор main_auth делает всю "магию" аутентификации за нас.
# on_start=True: пытается авторизоваться по параметрам из iframe (при первом открытии)
# on_cookies=True: пытается авторизоваться по кукам (при последующих открытиях)
# set_cookie=True: устанавливает куку в браузере после успешной авторизации "на старте"


@main_auth(on_start=True)
def index(request):
    """
    Главная страница прилложения
    декоратор @main-auth у нас автоматически обрабатывает аунтефикацию

    """
    bitrix_user = request.bitrix_user
    bitrix_user_token = request.bitrix_user_token

    # 1 - получаем имя пользователя из ллокальной БД
    user_name = f"{bitrix_user.first_name} {bitrix_user.last_name}"


    # 2 - получаем список сделок через API Bitrix24
    deals = []
    try:
        method = 'crm.deal.list'
        params = {
            'filter': {
                'ASSIGNED_BY_ID': bitrix_user.bitrix_id,
                'STAGE_ID': 'NEW'  # Только активные сделки
            },
            'select': [
                'ID',
                'TITLE',
                'OPPORTUNITY',
                'STAGE_ID',
                'BEGINDATE',
                'CLOSEDATE'
                'DELIVERY_ADDRESS',
            ],
            'order': {'DATE_CREATE': 'DESC'},
            'start': 0
        }
        api_response = bitrix_user_token.call_api_method(method, params)
        deals = api_response.get('result', [])[:10]
        # Форматируем даты для отображения
        for deal in deals:
            if deal.get('BEGINDATE'):
                deal['BEGINDATE_FORMATTED'] = format_date(deal['BEGINDATE'])
            if deal.get('CLOSEDATE'):
                deal['CLOSEDATE_FORMATTED'] = format_date(deal['CLOSEDATE'])

    except Exception as e:
        error_message = f'Ошибка получения сделок: {str(e)}'
        print(error_message)


    if request.method == 'POST':
        form = DealForm(request.POST)
        if form.is_valid():
            # подготтовка данных для создания сделки
            method = 'crm.deal.add'
            fields = {
                'TITLE': form.cleaned_data['title'],
                'OPPORTUNITY': form.cleaned_data['opportunity'],
                'ASSIGNED_BY_ID': bitrix_user.bitrix_id,
                'STAGE_ID': 'NEW',
                'BEGINDATE': form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
                'CLOSEDATE': form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
                'DELIVERY_ADDRESS': form.cleaned_data['delivery_address'],

            }
            params = {'fields': fields}

            # создание сделки через API
            try:
                create_response = bitrix_user_token.call_api_method(method, params)
                new_deal_id = create_response.get('result')

                if new_deal_id:
                    return redirect('index')
                else:
                    form.add_error(None, 'не удалось создать сделку')
            except Exception as e:
                form.add_error(None, f'Ошибка при создании сделки: {str(e)}')
    else:
        form = DealForm()
        success_message = None
        if 'success_message' in request.session:
            success_message = request.session.pop('success_message')
        context ={
            'user_name': user_name,
            'deals': deals,
            'form': form,
        }
        return render(request, 'index.html', context)
def format_date(date_string):
    """Форматирует дату из формата Bitrix24 в читаемый вид"""
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
        return date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        return date_string