import os
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

    results = [[] for _ in range(3)]
    for tr in parsed_html.body.find_all("tr"):
        tds = tr.find_all("td")[:3]
        for i, td in enumerate(tds):
            results[i].append(td.get_text(strip=True))

        if last_result in results[1]:
            break

    res_ids, res_courses, res_dates = results
    joined_result = ""
    for i, res_id in enumerate(res_ids):
        if i == len(res_ids) - 1:
            break
        joined_result += f"{res_id}. {res_courses[i]}\nResult date: {res_dates[i]}\n"

    message = f"Found results for\n{joined_result}\nClick here to view: https://onlineresults.unipune.ac.in/Result/Dashboard/Default"
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
    chat_id = "-1002176229957"
    payload = {"chat_id": chat_id, "text": message}

    result = requests.post(api + "/sendMessage", data=payload, timeout=5)
    if result.status_code != 200:
        print(result.text)


if __name__ == "__main__":
    main()
