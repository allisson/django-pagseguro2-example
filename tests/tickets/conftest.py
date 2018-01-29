from decimal import Decimal

import pytest

from apps.tickets.models import Event, Ticket, Cart, CartItem, Purchase


@pytest.fixture
def event():
    return Event.objects.create(title='My Event Title', description='My Event Description')


@pytest.fixture
def ticket(event):
    return Ticket.objects.create(event=event, title='My Ticket Title', price=Decimal('100.00'))


@pytest.fixture
def user(admin_user):
    return admin_user


@pytest.fixture
def cart(user):
    return Cart.objects.create(user=user, closed=False)


@pytest.fixture
def cart_item(cart, ticket):
    return CartItem.objects.create(cart=cart, ticket=ticket, quantity=1, unit_price=Decimal('100.00'))


@pytest.fixture
def purchase(cart_item):
    cart = cart_item.cart
    return Purchase.objects.create(user=cart.user, cart=cart, price=cart.price)


@pytest.fixture
def pagseguro_checkout_response():
    return '''<?xml version='1.0'?>
    <checkout>
      <code>36BCD3B352526D1EE4D6FFA359934D7E</code>
      <date>2018-01-27T10:11:28.000-02:00</date>
    </checkout>
    '''


@pytest.fixture
def pagseguro_checkout_error_response():
    return '''<?xml version='1.0'?>
    <errors>
      <error>
        <code>11029</code>
        <message>Some Error</message>
      </error>
    </errors>
    '''


@pytest.fixture
def pagseguro_notification():
    return {
        'notificationCode': 'E015A4E1F0D1F0D1594114997F98ED9736BA',
        'notificationType': 'transaction'
    }


@pytest.fixture
def pagseguro_transaction_response():
    return '''<?xml version='1.0' encoding='ISO-8859-1' standalone='yes'?>
    <transaction>
        <date>2018-01-29T12:27:57.000-02:00</date>
        <code>5479CBCF-2E8F-4594-A5E5-4BF2038C98C1</code>
        <reference>9fd05f66-315c-49f9-85f7-c92775f5a54d</reference>
        <type>1</type>
        <status>1</status>
        <lastEventDate>2018-01-29T12:34:05.000-02:00</lastEventDate>
        <paymentMethod>
            <type>1</type>
            <code>101</code>
        </paymentMethod>
        <grossAmount>700.00</grossAmount>
        <discountAmount>0.00</discountAmount>
        <feeAmount>35.33</feeAmount>
        <netAmount>664.67</netAmount>
        <extraAmount>0.00</extraAmount>
        <escrowEndDate>2018-01-29T12:34:05.000-02:00</escrowEndDate>
        <installmentCount>1</installmentCount>
        <itemCount>2</itemCount>
        <items>
            <item>
                <id>4ea9bfb9-98f0-498a-9e05-02028358f9c1</id>
                <description>Ticket 2</description>
                <quantity>2</quantity>
                <amount>200.00</amount>
            </item>
            <item>
                <id>fd7e1175-c50b-45b6-92b7-5e12bf550c8f</id>
                <description>Ticket 3</description>
                <quantity>1</quantity>
                <amount>300.00</amount>
            </item>
        </items>
        <sender>
            <name>Comprador Virtual</name>
            <email>c11004631206281776849@sandbox.pagseguro.com.br</email>
            <phone>
                <areaCode>11</areaCode>
                <number>999999999</number>
            </phone>
            <documents>
                <document>
                    <type>CPF</type>
                    <value>59586852873</value>
                </document>
            </documents>
        </sender>
        <shipping>
            <address>
                <street>RUA JOSE BRANCO RIBEIRO</street>
                <number>840</number>
                <complement></complement>
                <district>Catolé</district>
                <city>CAMPINA GRANDE</city>
                <state>PB</state>
                <country>BRA</country>
                <postalCode>58410175</postalCode>
            </address>
            <type>3</type>
            <cost>0.00</cost>
        </shipping>
        <gatewaySystem>
            <type>cielo</type>
            <rawCode xsi:nil='true' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'/>
            <rawMessage xsi:nil='true' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'/>
            <normalizedCode xsi:nil='true' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'/>
            <normalizedMessage xsi:nil='true' xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'/>
            <authorizationCode>0</authorizationCode>
            <nsu>0</nsu>
            <tid>0</tid>
            <establishmentCode>1056784170</establishmentCode>
            <acquirerName>CIELO</acquirerName>
        </gatewaySystem>
    </transaction>
    '''


@pytest.fixture
def pagseguro_transaction():
    return {
        'date': '2018-01-29T12:27:57.000-02:00',
        'code': '5479CBCF-2E8F-4594-A5E5-4BF2038C98C1',
        'reference': '9fd05f66-315c-49f9-85f7-c92775f5a54d',
        'type': '1',
        'status': '1',
        'lastEventDate': '2018-01-29T12:34:05.000-02:00',
        'paymentMethod': {
            'type': '1',
            'code': '101'
        },
        'grossAmount': '700.00',
        'discountAmount': '0.00',
        'feeAmount': '35.33',
        'netAmount': '664.67',
        'extraAmount': '0.00',
        'escrowEndDate': '2018-01-29T12:34:05.000-02:00',
        'installmentCount': '1',
        'itemCount': '2',
        'items': {
            'item': [
                {
                    'id': '4ea9bfb9-98f0-498a-9e05-02028358f9c1',
                    'description': 'Ticket 2',
                    'quantity': '2',
                    'amount': '200.00'
                },
                {
                    'id': 'fd7e1175-c50b-45b6-92b7-5e12bf550c8f',
                    'description': 'Ticket 3',
                    'quantity': '1',
                    'amount': '300.00'
                }
            ]
        },
        'sender': {
            'name': 'Comprador Virtual',
            'email': 'c11004631206281776849@sandbox.pagseguro.com.br',
            'phone': {
                'areaCode': '11',
                'number': '999999999'
            },
            'documents': {
                'document': {
                    'type': 'CPF',
                    'value': '59586852873'
                }
            }
        },
        'shipping': {
            'address': {
                'street': 'RUA JOSE BRANCO RIBEIRO',
                'number': '840',
                'complement': None,
                'district': 'Catol\u00e9',
                'city': 'CAMPINA GRANDE',
                'state': 'PB',
                'country': 'BRA',
                'postalCode': '58410175'
            },
            'type': '3',
            'cost': '0.00'
        },
        'gatewaySystem': {
            'type': 'cielo',
            'rawCode': {
                '@xsi:nil': 'true',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            },
            'rawMessage': {
                '@xsi:nil': 'true',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            },
            'normalizedCode': {
                '@xsi:nil': 'true',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            },
            'normalizedMessage': {
                '@xsi:nil': 'true',
                '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'
            },
            'authorizationCode': '0',
            'nsu': '0',
            'tid': '0',
            'establishmentCode': '1056784170',
            'acquirerName': 'CIELO'
        }
    }
