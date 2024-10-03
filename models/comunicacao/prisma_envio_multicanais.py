import requests


def send_message(instance_id, token, phone, message, tokenSeguranca):
    # Validação básica dos parâmetros
    if not instance_id or not token:
        print("Erro: instance_id e token são obrigatórios.")
        return
    if not phone or not message:
        print("Erro: phone e message são obrigatórios.")
        return

    url = f'https://api.z-api.io/instances/{instance_id}/token/{token}/send-text'
    headers = {
        'accept': '*/*',
        'client-token': tokenSeguranca,
        'Content-Type': 'application/json'
    }
    data = {
        'phone': phone,
        'message': message
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Levanta uma exceção para status code de erro
        print(f'Mensagem enviada com sucesso: {response.json()}')
    except requests.exceptions.HTTPError as errh:
        print(f'Erro HTTP: {errh.response.text}')
    except requests.exceptions.ConnectionError as errc:
        print(f'Erro de Conexão: {errc}')
    except requests.exceptions.Timeout as errt:
        print(f'Timeout: {errt}')
    except requests.exceptions.RequestException as err:
        print(f'Erro na requisição: {err}')


# Exemplo de uso
instance_id = '3D4DDF6D9902A0DFAA396A71C6EAAAAD'
token = 'A176AB914CE50FC259B73C58'
phone = '559883104384'
message = 'Hello World'
tokenSeguranca = 'F8e8e16f20c304066adf44faba08fa2ecS'

send_message(instance_id, token, phone, message, tokenSeguranca=tokenSeguranca)
