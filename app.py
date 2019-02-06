from flask import Flask, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

IMG_SIZE = (500, 200)
PROFILE_URL = 'https://www.acmicpc.net/user/'
STATUS_URL = 'https://www.acmicpc.net/status?user_id='
RANKING_URL = 'https://www.acmicpc.net/ranklist/'


def notosans(size):
    return ImageFont.truetype('NotoSansCJKkr-Regular.otf', size)


def slicing(str, limit):
    if len(str) <= limit:
        return str
    else:
        return str[:limit] + '...'


@app.route('/user/<string:username>')
def profile(username):
    # base image
    img = Image.new('RGB', IMG_SIZE, '#FFFFFF')
    logo = Image.open('logo.jpg').resize((30, 30))
    img.paste(logo, (465, 165))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 10, 200], fill='#0076C0')

    profile_soup = BeautifulSoup(requests.get(PROFILE_URL + username).text, 'html.parser')
    status_soup = BeautifulSoup(requests.get(STATUS_URL + username).text, 'html.parser')

    header_div = profile_soup.select('body > div.wrapper > div.container.content > div.row > div:nth-child(1) > div')[0]
    statics_table = profile_soup.select('#statics')[0]
    status_table = status_soup.select('#status-table')[0]

    username = header_div.find('h1').text.strip()
    comment = header_div.find('blockquote').text.strip()
    total_ranking = statics_table.find('th', text='랭킹').find_next_sibling().text.strip()
    solved = statics_table.find('th', text='푼 문제').find_next_sibling().text.strip()
    school_l = statics_table.find('th', text='학교/회사').find_next_sibling().text.strip().split()
    last_submission = status_table.select('tr:nth-child(1) > td:nth-child(9)')[0].text.strip()

    ranking_soup = BeautifulSoup(requests.get(RANKING_URL + str(int(total_ranking) // 100 + 1)).text, 'html.parser')
    ranking_table = ranking_soup.select('#ranklist')[0]
    ac_rate = ranking_table.select('tbody > tr:nth-child({}) > td:nth-child(6)'.format(int(total_ranking) % 100))[0].text.strip()

    print(ac_rate)

    draw.text((20, 0), username, 'black', font=notosans(40))
    draw.text((20, 55), slicing(comment, 30), 'gray', font=notosans(20))
    draw.text((20, 90), '마지막 제출 : ' + last_submission, 'gray', font=notosans(12))

    draw.text((20, 130), '푼 문제', 'gray', font=notosans(12))
    draw.text((20, 130), solved, 'gray', font=notosans(50))

    draw.text((20 + draw.textsize(solved, font=notosans(50))[0] + 40, 130), '전체 랭킹', 'gray', font=notosans(12))
    draw.text((20 + draw.textsize(solved, font=notosans(50))[0] + 40, 130), total_ranking, 'gray', font=notosans(50))

    draw.text((20 + draw.textsize(solved, font=notosans(50))[0] + 40 + draw.textsize(total_ranking, font=notosans(50))[0] + 40, 130), '정답 비율', 'gray', font=notosans(12))
    draw.text((20 + draw.textsize(solved, font=notosans(50))[0] + 40 + draw.textsize(total_ranking, font=notosans(50))[0] + 40, 130), ac_rate, 'gray', font=notosans(50))

    del draw

    # serve
    bytesIO = BytesIO()
    img.save(bytesIO, 'PNG')
    bytesIO.seek(0)
    return send_file(bytesIO, mimetype='image/png')


if __name__ == '__main__':
    app.run()
