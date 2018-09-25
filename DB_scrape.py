from bs4 import BeautifulSoup as bs
import requests
from calendar import monthrange
import DB_manager as dbm


def parsing_page():
    """
    Parse the webpage.
    Fisrt time of openning the link will get the link to other pages

        - month_links : a list of links to the pages of different monthes
    """

    # link of the page
    page_link = "https://skream.jp/live_info"
    # Defualt is the current month with lists of all possible concerts in all areas
    try:
        page_response = requests.get(page_link, timeout=5)
        if page_response.status_code == 200:
            try:
                page_content = bs(page_response.content, "html.parser")
            except:
                page_content = bs(page_response.content, "lxml")

            monthes = page_content.find(id="selectmonth")

            # Only extracts a half year long information
            month_links = [a['href'] for a in monthes.find_all('a', href=True)]

            main = page_content.find(id="main")

            get_data(main)

        else:
            print(page_response.status_code)
            print("ERROR")

    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))

    for link in month_links:
        try:
            # fetch the content form url
            # timeout is set to 5 seconds
            link = "https://skream.jp" + link
            page_response = requests.get(link)
            # If it is a successful http request
            if page_response.status_code == 200:
                # extract
                try:
                    page_content = bs(page_response.content, "html.parser")
                except:
                    page_content = bs(page_response.content, "lxml")
                # do some extraction in function

                main = page_content.find(id="main")

                get_data(main)

            else:
                print(page_response.status_code)
                print("ERROR")

        except requests.Timeout as e:
            print("It is time to timeout")
            print(str(e))

    db.DeleteSpecificRows()


def get_data(main):
    """get the folloing informations for each month:
        - Year
        - Month
        - Date
        - Band names
        - Area
        - Location
    and then store it to MySQL database"""

    date_text = main.find(id='date-text').find(text=True, recursive=False)
    # What year
    year = int(date_text[:4])
    # Which month
    month = int(date_text[5:7])
    print("year is: ", year)
    print("month is : ", month)

    # NEEDS TO CREATE A TABLE FOR EVERYMONTH

    # list of days in that month
    days = [i for i in range(1, monthrange(int(year), int(month))[1] + 1)]

    # Needs to create a dictionary of dictionary
    # {"1", {"Band name": "Location", "Band2": "Location"}, 2:}

    numDay = 1
    for day in days:
        # print("Day is ", day)

        idDay = "day" + str(numDay)
        # print(idDay)
        eachDay = main.find(id=idDay)

        # print(eachDay)
        bandDiv = ""
        try:
            bandDiv = eachDay.find_all("div", class_="liveblock")
        except:
            pass

        if bandDiv:
            for b in bandDiv:

                # print("----------------------")
                # print(b)
                # print("----------------------")
                bandN = b.find('a').contents[0]
                areaN = b.find('p')['class'][0]
                # Needs to convert into japanese character
                areaN = eng_to_jpn(areaN)
                placeN = b.find('p').contents[0]
                # print("---------------------")
                # print("band name is ", bandN, " and its area is ", areaN, "and place is ", placeN)
                db.InsertTable(year, month, day, bandN, areaN, placeN)

            # break

        numDay += 1


def eng_to_jpn(eng):
    '''
    Converting scareped area info from english to Japanese
    '''
    jpn = ""
    if eng == "kanto":
        jpn = "関東"
    elif eng == "kinki":
        jpn = "近畿"
    elif eng == "chubu":
        jpn = "中部"
    elif eng == "kyusyu":
        jpn = "九州"
    elif eng == "tohoku":
        jpn = "東北"
    elif eng == "chugoku":
        jpn = "中国"
    elif eng == "hokkaido":
        jpn = "北海道"
    elif eng == "okinawa":
        jpn = "沖縄"
    elif eng == "shikoku":
        jpn = "四国"
    else:
        jpn == "全て"

    return jpn


if __name__ == "__main__":
    db = dbm.DataBase()
    db.DeleteTableData()
    parsing_page()
