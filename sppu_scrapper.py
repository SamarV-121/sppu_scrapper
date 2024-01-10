import os
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

with open("cred.json", "w") as f:
    f.write(os.environ.get("FIREBASE_TOKEN"))

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


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

    last_result = firestore_get()

    for i, td in enumerate(parsed_html.find_all("td")):
        if i == 1:
            latest_result = td.get_text(strip=True)
            break

    if last_result != latest_result:
        print("Found new results")
        firestore_add(latest_result)
    else:
        print("No new results are available")
        return

    res = ""
    for tr in parsed_html.body.find_all("tr"):
        res += tr.get_text(strip=True) + "\n"
        if last_result in res:
            break

    message = f"Found results for\n{res}\nClick here to view: https://onlineresults.unipune.ac.in/Result/Dashboard/Default"
    print(message)
    telegram(message)


def firestore_add(course):
    payload = {"course": course}
    ref = db.collection("course_info").document("course").set(payload)
    print(ref)


def firestore_get():
    return (
        db.collection("course_info").document("course").get().to_dict().get("course")
    )


def telegram(message):
    api = f"https://api.telegram.org/bot{os.environ.get('TELEGRAM_TOKEN')}"
    chat_id = "-1001893841304"
    payload = {"chat_id": chat_id, "text": message}

    result = requests.post(api + "/sendMessage", data=payload, timeout=5)
    if result.status_code != 200:
        print(result.text)


if __name__ == "__main__":
    main()
