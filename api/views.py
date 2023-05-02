from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.db import connection

import hashlib

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

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
            query = 'SELECT merchant.name, payment.time, payment.amount ' \
                    'FROM payment, merchant, account ' \
                    'WHERE payer_account_id = %s AND payee_account_id = account.id AND account.user_id = merchant.user_id;'
            print(query)
            cursor.execute(query, [account_id])
            datas = dictfetchall(cursor)
        except Exception as e:
            print(e)
            return Response('Error', status=500)
    return Response(datas)
