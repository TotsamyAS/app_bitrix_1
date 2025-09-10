# crm_integration/views.py
from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from .forms import DealForm
from django.http import HttpResponse, JsonResponse
import datetime
import logging


logger = logging.getLogger(__name__)

# Временная функция для сохранения параметров аутентификации
def save_auth_params(request):
    """Сохраняет параметры аутентификации в сессии"""
    if 'AUTH_ID' in request.POST:
        request.session['AUTH_ID'] = request.POST['AUTH_ID']
    if 'REFRESH_ID' in request.POST:
        request.session['REFRESH_ID'] = request.POST['REFRESH_ID']
    if 'DOMAIN' in request.GET:
        request.session['DOMAIN'] = request.GET['DOMAIN']

# Временная функция для восстановления параметров аутентификации
def restore_auth_params(request):
    """Восстанавливает параметры аутентификации из сессии в GET/POST"""
    if 'AUTH_ID' in request.session:
        request.POST._mutable = True
        request.POST['AUTH_ID'] = request.session['AUTH_ID']
        request.POST._mutable = False
    if 'REFRESH_ID' in request.session:
        request.POST._mutable = True
        request.POST['REFRESH_ID'] = request.session['REFRESH_ID']
        request.POST._mutable = False

# Временная диагностическая view
def debug_request(request):
    """Показывает сырые данные запроса"""
    debug_info = {
        'method': request.method,
        'GET_params': dict(request.GET),
        'POST_params': dict(request.POST),
        'COOKIES': dict(request.COOKIES),
        'has_bitrix_user': hasattr(request, 'bitrix_user'),
        'has_bitrix_user_token': hasattr(request, 'bitrix_user_token'),
    }

    if hasattr(request, 'bitrix_user'):
        debug_info['bitrix_user'] = str(request.bitrix_user)
    if hasattr(request, 'bitrix_user_token'):
        debug_info['bitrix_user_token'] = str(request.bitrix_user_token)

    return JsonResponse(debug_info, json_dumps_params={'indent': 4})

@main_auth(on_start=True)
def index(request):
    """
    Главная страница прилложения
    декоратор @main-auth у нас автоматически обрабатывает аунтефикацию

    """

    try:

        bitrix_user = request.bitrix_user
        bitrix_user_token = request.bitrix_user_token
        if not 'UF_CRM_DELIVERY_ADDRESS' in bitrix_user_token.call_api_method('crm.deal.fields', {}).get('result',[]):
            api_response = bitrix_user_token.call_api_method('crm.deal.userfield.add', {
                'fields': {
                    'LABEL': "UF_CRM_DELIVERY_ADDRESS",
                    'USER_TYPE_ID': "string",
                    'FIELD_NAME': "UF_CRM_DELIVERY_ADDRESS",
                    'MULTIPLE': "N",
                    'MANDATORY': "N",
                    'SHOW_FILTER': "Y",
                    'SETTINGS': {
                        'DEFAULT_VALUE': "UNKNOWN",
                    }
                }
            })
            logger.info(f'Поле UF_CRM_DELIVERY_ADDRESS создано: {api_response}',)


        print("=== AUTH SUCCESS ===")
        print("bitrix_user:", bitrix_user)
        print("bitrix_user_token:", bitrix_user_token)
        print("====================")

        # 1. получаем имя пользователя
        user_name = f"{bitrix_user.first_name} {bitrix_user.last_name}"


        # 2 - получаем список сделок через API Bitrix24
        deals = []
        try:
            method = 'crm.deal.list'
            params = {
                'filter': {
                    'ASSIGNED_BY_ID': bitrix_user.bitrix_id,
                    'STAGE_ID': 'NEW'  # только активные сделки
                },
                'select': [
                    'ID',
                    'TITLE',
                    'OPPORTUNITY',
                    'STAGE_ID',
                    'BEGINDATE',
                    'CLOSEDATE',
                    'UF_CRM_DELIVERY_ADDRESS',
                ],
                'order': {'DATE_CREATE': 'DESC'},
                'start': 0
            }
            api_response = bitrix_user_token.call_api_method(method, params)
            deals = api_response.get('result', [])[:10]

            print("Поля 10-й сделки:", deals[9].keys() if deals else "Нет сделок")
            # форматирование даты для отображения
            for deal in deals:
                if deal.get('BEGINDATE'):
                    deal['BEGINDATE_FORMATTED'] = format_date(deal['BEGINDATE'])
                if deal.get('CLOSEDATE'):
                    deal['CLOSEDATE_FORMATTED'] = format_date(deal['CLOSEDATE'])

        except Exception as e:
            error_message = f'Ошибка получения сделок: {str(e)}'
            logger.error(error_message)


        if request.method == 'POST':
            # if 'AUTH_ID' not in request.POST:
                # restore_auth_params(request)
                # logger.info('перенастройка параметров авторизации во время POST...')
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
                    'UF_CRM_DELIVERY_ADDRESS': form.cleaned_data['delivery_address'],

                }
                params = {'fields': fields}

                # создание сделки через API
                try:
                    api_response = bitrix_user_token.call_api_method(method, params)
                    new_deal_id = api_response.get('result')

                    if new_deal_id:
                        # УСПЕХ: обновить список сделок после успешного создания
                        try:
                            method = 'crm.deal.list'
                            params = {
                                'filter': {
                                    'ASSIGNED_BY_ID': bitrix_user.bitrix_id,
                                    'STAGE_ID': 'NEW'
                                },
                                'select': [
                                    'ID',
                                    'TITLE',
                                    'OPPORTUNITY',
                                    'STAGE_ID',
                                    'BEGINDATE',
                                    'CLOSEDATE',
                                    'UF_CRM_DELIVERY_ADDRESS',
                                ],
                                'order': {'DATE_CREATE': 'DESC'},
                                'start': 0
                            }
                            api_response = bitrix_user_token.call_api_method(method, params)
                            deals = api_response.get('result', [])[:10]

                            for deal in deals:
                                if deal.get('BEGINDATE'):
                                    deal['BEGINDATE_FORMATTED'] = format_date(deal['BEGINDATE'])
                                if deal.get('CLOSEDATE'):
                                    deal['CLOSEDATE_FORMATTED'] = format_date(deal['CLOSEDATE'])

                        except Exception as e:
                            logger.error(f'Ошибка при обновлении списка сделок: {e}')
                except Exception as e:
                    form.add_error(None, f'Ошибка при создании сделки: {str(e)}')
                    deals = []
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
        response = render(request, 'index.html', context)
        return response
    except Exception as e:
        return HttpResponse( f'Ошибка в основном обработчике: {str(e)}')

# Простая функция для проверки, что сервер работает
def health_check(request):
    return HttpResponse("Server is running!")
def format_date(date_string):
    """Форматирует дату из формата Bitrix24 в читаемый вид"""
    try:
        date_obj = datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')
        return date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        return date_string

