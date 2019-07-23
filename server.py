"""api, возвращающее изображения и их превью 100x100 пикселей"""
from os import chdir
from base64 import b64encode
from tempfile import TemporaryDirectory
from flask import Flask, jsonify, request
from PIL import Image
from requests import get

def encode_img(img_filename):
    """преобразование файла в base64"""
    img = open(img_filename, "rb")
    img_read = img.read()
    img_64_encode = b64encode(img_read)
    return img_64_encode

def download(url):
    """скачивание и сохранение файла по ссылке"""
    img = get(url)
    out = open('img.jpeg', "wb")
    out.write(img.content)
    out.close()

def make_preview(img_filename):
    """создание превью 100x100 пикселей из файла в папке"""
    img = Image.open(img_filename)
    width = img.size[0]
    height = img.size[1]
    #обрезание до квадратной формы
    if width == height:
        pass
    elif width > height:
        difference = (width - height)//2
        img = img.crop((difference, 0, width-difference, height))
    elif height > width:
        difference = (height - width)//2
        img = img.crop((0, difference, width, height-difference))
    #изменение размера
    img = img.resize((100, 100), Image.ANTIALIAS)
    #сохранение нового файла
    img.save("img-preview.jpeg")
    img.close()

APP = Flask(__name__)

@APP.route('/img_api/v1.0', methods=['POST'])
def images():
    """основная функция api"""
    url_list = request.json['url_list']
    img_list = []
    preview_list = []
    for img_url in url_list:
        #создание временной директории
        #чтобы не было путаницы в названии файлов при каждой итерации url_list
        with TemporaryDirectory() as directory:
            chdir(directory)
            download(img_url)
            img_list.append(encode_img("img.jpeg"))
            make_preview("img.jpeg")
            preview_list.append(encode_img("img-preview.jpeg"))
    response_dict = {'original':img_list, 'previews':preview_list}
    return jsonify({'images':response_dict})

if __name__ == '__main__':
    APP.run(debug=True)
