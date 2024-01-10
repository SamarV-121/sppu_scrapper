import os
import requests
from bs4 import BeautifulSoup


def main():
    html = requests.get(
        "https://onlineresults.unipune.ac.in/Result/Dashboard/Default",
        verify=False,
        timeout=10,
    )

    if html.status_code == 200:
        parsed_html = BeautifulSoup(html.content, features="lxml")
    else:
        print(html.status_code)
        return

    if not os.path.exists("last"):
        open("last", "w", encoding="utf-8").close()

    with open("last", "r", encoding="utf-8") as f:
        last_result = f.read()

    for i, td in enumerate(parsed_html.find_all("td")):
        if i == 1:
            latest_result = td.get_text(strip=True)
            break

    with open("last", "w", encoding="utf-8") as f:
        if last_result != latest_result:
            print("Found new results")
            f.write(latest_result)
        else:
            print("No new results are available")
            f.write(last_result)
            return

    res = ""
    for tr in parsed_html.body.find_all("tr"):
        res += tr.get_text(strip=True) + "\n"
        if last_result in res:
            break

    message = f"Found results for\n{res}\nClick here to view: https://onlineresults.unipune.ac.in/Result/Dashboard/Default"
    print(message)
    telegram(message)


def telegram(message):
    api = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_TOKEN')}"
    chat_id = "-1001893841304"
    payload = {"chat_id": chat_id, "text": message}

    result = requests.post(api + "/sendMessage", data=payload, timeout=5)
    if result.status_code != 200:
        print(result.text)


if __name__ == "__main__":
    main()
