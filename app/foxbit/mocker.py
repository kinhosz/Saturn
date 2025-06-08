import json
import os
import random, requests
import time
from datetime import datetime, timezone
from ..constant import env_name


''' Exporting method '''
def mocker(func):
    ''' This decorator helps to development environment, avoiding
        making real authenticated requests'''
    async def wrapper(cls, method, url, headers, params, json):
        if env_name() != 'development':
            return await func(cls, method, url, headers, params, json)

        return handle_requests(method, url, headers, params, json)
    return wrapper

''' Mocked class for requests lib '''
class Response:
    def __init__(self, data, status):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data

def route_match(client_url, client_method, server_url, server_method):
    ''' checks if requested and route are the same resource '''
    if client_method != server_method:
        return False

    req_resources = client_url.split('/')
    route_resources = server_url.split('/')

    if len(req_resources) != len(route_resources):
        return False

    for req_r, route_r in zip(req_resources, route_resources):
        if len(route_r) > 0 and route_r[0] == '$':
            continue
        if req_r != route_r:
            return False

    return True

def handle_requests(method, url, headers, params, json):
    ''' Handle requests: List of all simulated responses from Foxbit '''

    resource = 'https://api.foxbit.com.br/rest/v3/markets/$market_symbol/candlesticks'
    if route_match(url, method, resource, 'GET'):
        return execute_get_candlesticks()

    resource = 'https://api.foxbit.com.br/rest/v3/orders'
    if route_match(url, method, resource, 'POST'):
        return execute_create_order(json)

    resource = 'https://api.foxbit.com.br/rest/v3/orders/by-order-id/$id'
    if route_match(url, method, resource, 'GET'):
        return execute_get_order_by_id(url)

    return Response({}, 500)

def execute_public_request(method, url, headers, params, json):
    ''' Executing requests that auth is not needed '''
    return requests.request(method, url, headers=headers, params=params, json=json)

def execute_get_candlesticks():
    ''' Mocking get_candlesticks for user input '''

    price = input("Type the current price: ")
    data = [
        [
            "1692918000000",
            str(price),
            str(price),
            str(price),
            str(price),
            "1692918060000",
            "0.17080431",
            "21866.35948786",
            66,
            "0.12073605",
            "15466.34096391"
        ]
    ]

    return Response(data, 200)

def execute_create_order(data):
    ''' Creating an order - json type '''

    id = time.time_ns() // 10**6
    order = {
        'id': id,
        'client_order_id': data.get('client_order_id', None),
        'market_symbol': data.get('market_symbol'),
        'side': data.get('side'),
        'type': data.get('type'),
        'state': 'ACTIVE',
        'price': data.get('price', None),
        'price_avg': "0.0",
        'quantity': data.get('quantity'),
        'quantity_executed': "0.0",
        'instant_amount': None,
        'instant_amount_executed': None,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'trades_count': 0,
        'remark': data.get('remark', ''),
        'funds_received': "0.0",
        'fee_paid': "0.0",
        'post_only': False,
        'time_in_force': "GTC",
        'cancellation_reason': None,
    }
    save(order)

    res_data = { 'id': order['id'], 'client_order_id': order['client_order_id'] }
    return Response(res_data, 201)

def execute_get_order_by_id(url):
    id = int(url.split('/')[-1])

    process_orders()
    orders = get_orders()

    res_order = None
    for order in orders:
        if order['id'] == id:
            res_order = order

    if not res_order:
        return Response({}, 404)

    return Response(order, 200)


''' Simulators of internal foxbit process '''
def process_orders():
    ''' Changing order state '''

    def apply_taxes(order):
        quantity_executed = float(order.get('quantity_executed', 0.0))        
        if order['side'] == 'BUY':
            fee_paid = quantity_executed * 0.005
            order['quantity_executed'] = str(quantity_executed - fee_paid)
        else:
            fee_paid = (float(order['price_avg']) * float(order['quantity_executed'])) * 0.005
        order['fee_paid'] = str(fee_paid)

    def add_trade(order, quantity):
        perc_diff = random.uniform(0.0, 0.01)
        perc = 1.0 + (perc_diff if order['side'] == 'SELL' else -perc_diff)
        current_price = float(order['price']) * perc
        executed_price = float(order['price_avg'])

        order['trades_count'] += 1
        order['price_avg'] = str((
            executed_price * float(order['quantity_executed']) + current_price * quantity
        ) / (float(order['quantity_executed']) + quantity))
        order['quantity'] = str(float(order['quantity']) - quantity)
        order['quantity_executed'] = str(float(order['quantity_executed']) + quantity)

    orders = get_orders()
    for order in orders:
        if order['state'] in ('FILLED', 'PARTIALLY_CANCELED', 'CANCELED'):
            continue

        next_states = ['FILLED', 'PARTIALLY_FILLED'] * 3
        if order['state'] == 'ACTIVE':
            next_states += ['ACTIVE'] * 3
            next_states += ['CANCELED']
        elif order['state'] == 'PARTIALLY_FILLED':
            next_states += ['PARTIALLY_CANCELED']

        order['state'] = random.choice(next_states)

        if order['state'] == 'CANCELED':
            order['cancellation_reason'] = 1

        elif order['state'] == 'PARTIALLY_CANCELED':
            order['cancellation_reason'] = 1
            apply_taxes(order)

        elif order['state'] == 'PARTIALLY_FILLED':
            add_trade(order, float(order['quantity']) / 2.0)

        elif order['state'] == 'FILLED':
            add_trade(order, float(order['quantity']))
            apply_taxes(order)

    write(orders)

'''
    Helpers to write / read on file
'''

DIR = '.foxbit_bin'

def ensure_dir():
    if not os.path.exists(DIR):
        os.makedirs(DIR)

def save(order):
    ''' Save the data into a json file on the system '''
    orders = get_orders()
    orders.append(order)
    write(orders)

def write(orders):
    ensure_dir()
    with open(f"{DIR}/orders.json", "w") as f:
        json.dump(orders, f, indent=4)

def get_orders():
    try:
        with open(f"{DIR}/orders.json", "r") as f:
            content = json.loads(f.read())
    except FileNotFoundError:
        content = []

    return content
