from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import connection
from django.core.cache import cache

import hashlib

from .utils import status_dict, gender_dict, calculate_age, dictfetchall

@api_view(['GET'])
def index_test(request):
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': 'Welcome'})

@api_view(['POST'])
def create_user(request):
    data = request.data
    
    if data['userType'] not in ['individual', 'merchant']:
        return Response('Unknown user type', status=500)
    
    password = hashlib.sha1(data['password'].encode('utf-8')).hexdigest()
    
    with connection.cursor() as cursor:
        try:
            # 检查user是否已经存在
            query = 'SELECT * FROM user ' \
                    'WHERE mobile_number = %s;'
            cursor.execute(query, [data['mobileNumber']])
            row = cursor.fetchone()
            if row is not None:
                return Response({'errCode': 1, 'errMsg': 'User already exists'})
            
            # 创建user
            query = 'INSERT INTO user' \
                    '(mobile_number, password)' \
                    'VALUES' \
                    '(%s, %s)'
            cursor.execute(query, [data['mobileNumber'], password])
            
            # 查询user_id
            query = 'SELECT * FROM user WHERE mobile_number = %s'
            cursor.execute(query, [data['mobileNumber']])
            user_id = cursor.fetchone()[0]
            
            # 创建account
            query = 'INSERT INTO account' \
                    '(status, balance, user_id)' \
                    'VALUES' \
                    '(%s, %s, %s)'
            cursor.execute(query, ['normal', 0.0, user_id])
            
            # 创建individual或merchant
            if data['userType'] == 'individual':
                query = 'INSERT INTO individual ' \
                        '(name, gender, birthday, user_id) ' \
                        'VALUES' \
                        '(%s, %s, %s, %s);'
                gender = data['gender'] if data['gender'] != 'unknown' else None
                cursor.execute(query, [data['name'], gender, data['birthday'], user_id])
                
        except:
            return Response('Failed', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful'})

@api_view(['POST'])
def authenticate_user(request):
    data = request.data
    password = hashlib.sha1(data['password'].encode('utf-8')).hexdigest()
    with connection.cursor() as cursor:
        try:
            query = 'SELECT * FROM user WHERE mobile_number=%s'
            cursor.execute(query, [data['mobileNumber']])
            row = cursor.fetchone()
            if row is not None:
                if row[2] == password:
                    result = 'pass'
                else:
                    result = 'fail'
            else:
                result = 'unknown'
        except:
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': result}, status=200)

@api_view(['POST'])
def get_account_ids(request):
    data = request.data
    mobile_number = data['mobileNumber']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT id FROM user WHERE mobile_number = %s'
            cursor.execute(query, [mobile_number])
            rows = cursor.fetchall()
            ids = [row[0] for row in rows]
        except:
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': ids})

@api_view(['POST'])
def get_account_balance(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT balance FROM account WHERE id = %s'
            cursor.execute(query, [account_id])
            row = cursor.fetchone()
            balance = str(row[0])
        except:
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': balance})

@api_view(['POST'])
def get_account_payment_preview(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'CALL get_account_payment_preview(%s);'
            cursor.execute(query, [account_id])
            datas = dictfetchall(cursor)
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': datas})

@api_view(['POST'])
def get_account_info(request):
    data = request.data
    account_id = data['accountId']
    info = []
    with connection.cursor() as cursor:
        try:
            query = 'SELECT account.status, individual.name, individual.gender, individual.birthday, user.mobile_number ' \
                    'FROM account, individual, user ' \
                    'WHERE account.id = %s AND account.user_id = user.id AND individual.user_id = user.id;'
            cursor.execute(query, [account_id])
            row = cursor.fetchone()
            info.append({'title': '账户状态', 'content': status_dict[row[0]]})
            info.append({'title': '姓名', 'content': row[1]})
            info.append({'title': '性别', 'content': gender_dict[row[2]]})
            info.append({'title': '年龄', 'content': str(calculate_age(row[3]))})
            info.append({'title': '手机号码', 'content': row[4]})
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': info})

@api_view(['POST'])
def edit_account_info(request):
    data = request.data
    account_id = data['accountId']
    name = data['name']
    gender = data['gender'] if data['gender'] != 'unknown' else None
    birthday = data['birthday']
    with connection.cursor() as cursor:
        try:
            query = 'CALL edit_account_info(%s, %s, %s, %s)'
            cursor.execute(query, [account_id, name, gender, birthday])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful'})

@api_view(['POST'])
def get_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT number, type, expiration_date as expirationDate, bank_name as bankName ' \
                    'FROM bank_card ' \
                    'WHERE account_id = %s;'
            cursor.execute(query, [account_id])
            datas = dictfetchall(cursor)
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': datas})

@api_view(['POST'])
def delete_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    number = data['number']
    with connection.cursor() as cursor:
        try:
            query = 'CALL delete_account_bank_card(%s, %s);'
            cursor.execute(query, [account_id, number])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful'})

@api_view(['POST'])
def add_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT * FROM bank_card ' \
                    'WHERE number = %s;'
            cursor.execute(query, [data['number']])
            row = cursor.fetchone()
            if row is not None:
                return Response({'errCode': 1, 'errMsg': 'Bank card number already exists'})

            query = 'CALL add_account_bank_card(%s, %s, %s, %s, %s);'
            cursor.execute(query, [account_id, data['number'], data['type'], data['expirationDate'], data['bankName']])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response({'errCode': 0, 'errMsg': 'Successful'})

@api_view(['POST'])
def create_temp_payment(request):
    data = request.data
    account_id, token = data['accountId'], data['token']
    cache_key = f'{account_id}_{token}'
    cache.set(cache_key, {'payer_account_id': None, 'payee_account_id': account_id, 'status': 'waiting'}, timeout=10)
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': cache_key})

@api_view(['POST'])
def renewal_temp_payment(request):
    data = request.data
    account_id, token = data['accountId'], data['token']
    cache_key = f'{account_id}_{token}'
    cache.expire(cache_key, timeout=10)
    if cache.ttl(cache_key) == 0:
        return Response({'errCode': 1, 'errMsg': 'Temp payment not exist'})
    return Response({'errCode': 0, 'errMsg': 'Successful'})

@api_view(['POST'])
def get_temp_payment_status(request):
    data = request.data
    cache_key = data['tempPaymentKey']
    cache.expire(cache_key, timeout=10)
    if cache.ttl(cache_key) == 0:
        return Response({'errCode': 1, 'errMsg': 'Temp payment not exist'})
    return Response({'errCode': 0, 'errMsg': 'Successful', 'data': cache.get(cache_key)['status']})
