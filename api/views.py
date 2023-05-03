from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import connection

import hashlib

from .utils import status_dict, gender_dict, calculate_age, dictfetchall

@api_view(['GET'])
def index_test(request):
    with connection.cursor() as cursor:
        try:
            cursor.execute('abcd;')
        except:
            return Response('Failed', status=404)
    return Response('Success')

@api_view(['POST'])
def create_user(request):
    data = request.data
    
    if data['userType'] not in ['individual', 'merchant']:
        return Response('Unknown user type', status=500)
    
    password = hashlib.sha1(data['password'].encode('utf-8')).hexdigest()
    
    with connection.cursor() as cursor:
        try:
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
    return Response('Successful')

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
    return Response(result, status=200)

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
    return Response(ids)

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
    return Response({'balance': balance})

@api_view(['POST'])
def get_account_payment_preview(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT payment.id, merchant.name, payment.time, payment.amount ' \
                    'FROM payment, merchant, account ' \
                    'WHERE payer_account_id = %s AND payee_account_id = account.id AND account.user_id = merchant.user_id;'
            cursor.execute(query, [account_id])
            datas = dictfetchall(cursor)
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response(datas)

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
            info.append({'title': '用户状态', 'content': status_dict[row[0]]})
            info.append({'title': '姓名', 'content': row[1]})
            info.append({'title': '性别', 'content': gender_dict[row[2]]})
            info.append({'title': '年龄', 'content': str(calculate_age(row[3]))})
            info.append({'title': '手机号码', 'content': row[4]})
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response(info)

@api_view(['POST'])
def edit_account_info(request):
    data = request.data
    account_id = data['accountId']
    name = data['name']
    gender = data['gender'] if data['gender'] != 'unknown' else None
    birthday = data['birthday']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT individual.id '\
                    'FROM individual, account '\
                    'WHERE account.id = %s AND account.user_id = individual.user_id;'
            cursor.execute(query, [account_id])
            individual_id = cursor.fetchone()[0]
            
            query = 'UPDATE individual '\
                    'SET name = %s, gender = %s, birthday = %s '\
                    'WHERE id = %s;'
            cursor.execute(query, [name, gender, birthday, individual_id])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response('Successful')

@api_view(['POST'])
def get_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'SELECT number, type, expiration_date as expirationDate , bank_name as bankName FROM bank_card '\
                    'WHERE account_id = %s;'
            cursor.execute(query, [account_id])
            datas = dictfetchall(cursor)
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response(datas)

@api_view(['POST'])
def delete_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    number = data['number']
    with connection.cursor() as cursor:
        try:
            query = 'DELETE FROM bank_card ' \
                    'WHERE account_id = %s AND number = %s;'
            cursor.execute(query, [account_id, number])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response('Successful')

@api_view(['POST'])
def add_account_bank_card(request):
    data = request.data
    account_id = data['accountId']
    with connection.cursor() as cursor:
        try:
            query = 'INSERT INTO bank_card ' \
                    '(account_id, number, type, expiration_date, bank_name) ' \
                    'VALUES ' \
                    '(%s, %s, %s, %s, %s);'
            cursor.execute(query, [account_id, data['number'], data['type'], data['expirationDate'], data['bankName']])
            
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response('Successful')
