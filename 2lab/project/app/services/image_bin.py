import base64
from PIL import Image
from io import BytesIO
import numpy as np


def from_b64(b64):
    decoded_string = base64.b64decode(b64)
    image = Image.open(BytesIO(decoded_string))
    data = image.load()
    return data, image.size[0], image.size[1]


def pil_to_gray_array(pix_data, width, height):
    res = np.zeros((width, height))
    for i in range(width):
        for j in range(height):
            r, g, b = pix_data[i, j][:3]
            gray = 0.2125*r + 0.7154*g + 0.0721*b
            res[i, j] = gray
    return res.reshape(1, -1)[0], width, height


def bradley_rot(im, width, height):
    S = width // 8
    s2 = S // 2
    t = 0.15
    integral_image = np.zeros((width, height))

    # Рассчитываем интегральное изображение
    for i in range(width):
        sum = 0
        for j in range(height):
            index = j * width + i
            sum += im[index]
            if i == 0:
                integral_image[i, j] = sum
            else:
                integral_image[i, j] = integral_image[i - 1, j] + sum

    res = np.zeros_like(im)

    # Находим границы для локальных областей
    for i in range(width):
        for j in range(height):
            index = j * width + i

            x1 = max(i - s2, 0)
            x2 = min(i + s2, width - 1)
            y1 = max(j - s2, 0)
            y2 = min(j + s2, height - 1)

            count = (x2 - x1) * (y2 - y1)
            sum_local = (integral_image[x2, y2] - integral_image[x2, y1] - integral_image[x1, y2]
                         + integral_image[x1, y1])

            if (im[index] * count) < (sum_local * (1.0 - t)):
                res[index] = 0
            else:
                res[index] = 255

    return res.reshape(width, height)


def convert_to_im(arr):
    im_from_arr = Image.fromarray(np.transpose(arr))
    return im_from_arr


def to_b64(im):
    buffered = BytesIO()
    converted = im.convert('RGB')
    converted.save(buffered, format='png')
    im_bytes = buffered.getvalue()
    im_b64 = base64.b64encode(im_bytes).decode('utf-8')
    return im_b64


def all_the_bradley(im_raw_b64):
    gray_im = pil_to_gray_array(*from_b64(im_raw_b64))
    bradley_rot_arr = bradley_rot(*gray_im)
    new_img = convert_to_im(bradley_rot_arr)
    im_b64 = to_b64(new_img)
    return im_b64


def test_im(im_in_b64):
    im_bytes = base64.b64decode(im_in_b64)
    im_file = BytesIO(im_bytes)
    img = Image.open(im_file)
    img.show()


# # получаем строку в формате b64 для нашей image:
# with open('31.68.jpeg', 'rb') as img:
#     encoded_string = base64.b64encode(img.read())
# print(encoded_string)


# # тестируем ту строку b64, что получили:
# to_test =
# test_im(to_test)
