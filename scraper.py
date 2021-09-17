from bs4 import BeautifulSoup
import lxml
import requests
import time
import os
import concurrent.futures
import json
from urllib.parse import unquote


mainURL = "https://anime1.me/category/2020%e5%b9%b4%e5%86%ac%e5%ad%a3/%e9%ad%94%e6%b3%95%e7%b4%80%e9%8c%84-%e9%ad%94%e6%b3%95%e5%b0%91%e5%a5%b3%e5%b0%8f%e5%9c%93%e5%a4%96%e5%82%b3"
apiURL = "https://v.anime1.me/api"

headers = {
    "Referer": '',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47",
    "Origin": "https://v.anime1.me"
}


videoHeader = {
    "Referer": 'https://v.anime1.me/',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.47",
    "Cookie": ""
}


forms = {
    "d": ""
}


def thread(session, middleURL):
    videoTitle = ""
    ss = session.post(middleURL)
    videoSoup = BeautifulSoup(ss.content, "lxml")
    mainScript = videoSoup.findAll("script")[-1].string

    str = mainScript.split(
        "p.setup({")[-1].split("});")[0].replace("\n", "").replace(" ", "")

    while True:
        arr = str.split(":", 1)
        val = arr[-1].split(",", 1)

        if arr[0] == "title":
            videoTitle = val[0].replace("\"", "").replace("\'", "")
            break
        str = val[-1]

    d = unquote(mainScript.split(
        "x.send('d=")[-1].split("');")[0].replace("\n", "").replace(" ", ""))

    forms["d"] = d
    headers["Referer"] = middleURL

    try:
        with requests.Session() as newSession:
            getVideoURL = newSession.post(apiURL, data=forms, headers=headers)
            videoHeader["Cookie"] = json.dumps(getVideoURL.cookies.get_dict()).split(
                "{", 1)[-1].split("}", 1)[0].replace("\"", "").replace(" ", "").replace(",", "; ").replace(":", "=")
            urlObj = json.loads(getVideoURL.content)
            time.sleep(10)
            videoContent = newSession.get(
                "https:"+urlObj['l'], headers=videoHeader)

            if videoContent.status_code == 200:
                print(videoTitle, " 成功")
                with open("./videos/"+videoTitle+".mp4", 'wb') as f:
                    f.write(videoContent.content)
                    f.close()

                    print("the header is ", videoHeader)
                    print("\n\n\n\n\n\n\n\n")
            else:
                print("FAILED!!!!!!!")
                print("the title is ", videoTitle)
                print("the header is ", videoHeader)
                print("the url is ", "https:"+urlObj['l'])
                print("the code is ", videoContent)
                print("\n\n\n\n")

    except Exception as e:
        print(e)


def pool(session, middleURLs):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        all_task = [executor.submit(thread, session, middleURL)
                    for middleURL in middleURLs]
        wait(all_task, return_when=ALL_COMPLETED)


def scraper():
    with requests.Session() as s:
        res = s.get(mainURL)
        soup = BeautifulSoup(res.content, "lxml")
        iframes = soup.findAll("iframe", {"class": "vframe"})
        middleURLs = list(map(lambda iframe: iframe["src"], iframes))
        # if 上一頁的話就要在往下找

        pool(session=s, middleURLs=middleURLs)


def cls(): return os.system('cls')


def main():
    # cls()
    scraper()


if __name__ == '__main__':
    main()
