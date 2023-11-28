import tls_client
import os
import sys
import json
import csv
import questionary
from questionary import Choice



cwd = os.getcwd()

file_wallets = f'{cwd}/wallets.txt'

with open(file_wallets, 'r') as file:
    WALLETS = [row.strip().lower() for row in file]


def get_module():
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice("1) Zksync", 1),
            Choice("2) Base", 2),
            Choice("3) Zora", 3),
            Choice("4) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        sys.exit()
    return result


def setup_session() -> tls_client.Session:
    session = tls_client.Session(
        client_identifier="chrome112",
        random_tls_extension_order=True
    )

    headers = {
        'origin': 'https://dune.com',
        'referer': 'https://dune.com/',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    session.headers = headers
    session.timeout_seconds = 1000
    return session


def get_data(chain, query) -> None:
    file_result = f'{cwd}/results/{chain}.csv'

    file_query = f'{cwd}/files/{query}.json'

    session = setup_session()

    print('Загрузка данных dune. Процесс может занять несколько минут...')

    with open(file_query, 'r') as file:
        payload = json.load(file)

    while True:
        try:
            response = session.post('https://app-api.dune.com/v1/graphql', json=payload)
            if (response.status_code == 200):
                break
            else:
                print(f'Ошибка загрузки базы данных: {response.text} | Cтатус запроса: {response.status_code}')
        except Exception as error:
            print(f'Ошибка загрузки базы данных: {error}')

    response_json = response.json()

    input_dict = response_json['data']['get_execution']['execution_succeeded']['data']

    output_dict = [x for x in input_dict if x['user_address'] in WALLETS]
    rows = []
    
    print('Запись результат в файл...')

    for wallet_data in output_dict:
       rows.append(wallet_data.values())
    
    Details = wallet_data.keys()

    with open(f'{file_result}', 'w', newline='') as csvfile:
        write = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        write.writerow(Details)

        write.writerows(rows)        

    print(f'Готово!\n')


def base() -> None:
    get_data("Base", "query_base")


if __name__ == '__main__':
    #module = get_module()
    base()
