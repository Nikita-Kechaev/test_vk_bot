import os
import sqlite3

import vk_api
from dotenv import load_dotenv
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

load_dotenv()

API_GROUP_TOKEN = os.getenv('API_GROUP_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
CALLBACK_TYPES = ('show_snackbar', 'open_link', 'open_app')


def cr_sql_db():
    """
    Создает SQLite - ДБ с 2мя таблицами.
    """
    connection = sqlite3.connect('product_db')
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product_type(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL);
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS product(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            image_url TEXT NOT NULL,
            product_type_id INTEGER,
            FOREIGN KEY (product_type_id)  REFERENCES product_type(id));
        """
    )
    connection.commit()
    cursor.close()


def fill_db():
    """
    Наполняет DB тестовыми данными.
    """
    type_1 = (1, 'Пирожки')
    type_2 = (2, 'Торты')
    type_3 = (3, 'Пицца')
    type_4 = (4, 'Печенье')
    product_1 = (
        1,
        'Пирожок с капустой',
        'Вкусный пирожок с капустой за 15р',
        'img/kapusta.jpg',
        1
    )
    product_2 = (
        2,
        'Пирожок с картошкой',
        'Вкусный пирожок с картошкой за 20р',
        'img/kartoshka.jpg',
        1
    )
    product_3 = (
        3,
        'Торт мачо',
        'Вкусный торт за 100р',
        'img/macho.jpg',
        2
    )
    product_4 = (
        4,
        'Родня Макрона',
        'Вкусный Наполеон за 100р',
        'img/Napoleon.jpg',
        2
    )
    product_5 = (
        5,
        'Пиица бабушкина',
        'Пицца как у бабушки!',
        'img/babushka_pizza.jpeg',
        3
    )
    product_6 = (
        6,
        'Пицца от деда',
        'Пицца от деда за 20р',
        'img/ded_pizza.jpg',
        3
    )
    product_7 = (
        7,
        'Печенье шоколадное',
        'Печенька шок. 100р',
        'img/pech_shok.jpg',
        4
    )
    product_8 = (
        8,
        'Печенька обычная',
        'Очень вкусная печенька!',
        'img/pech_ob.jpeg',
        4
    )
    type_list = [type_1, type_2, type_3, type_4]
    product_list = [
        product_1,
        product_2,
        product_3,
        product_4,
        product_5,
        product_6,
        product_7,
        product_8
    ]
    connection = sqlite3.connect('product_db')
    cursor = connection.cursor()
    sqlite_insert_pruduct_type = """INSERT INTO product_type
                              (id,
                               type)
                              VALUES (?, ?);"""
    sqlite_insert_pruduct = """INSERT INTO product
                              (id,
                               name,
                               description,
                               image_url,
                               product_type_id)
                              VALUES (?, ?, ?, ?, ?);"""
    for elem in type_list:
        cursor.execute(sqlite_insert_pruduct_type, elem)
    for elem in product_list:
        cursor.execute(sqlite_insert_pruduct, elem)
    connection.commit()
    cursor.close()


def db_get_products_types():
    """
    Получает из БД типы товаров.
    """
    connection = sqlite3.connect('product_db')
    cursor = connection.cursor()
    sqlite_querry = """
    select * from product_type"""
    cursor.execute(sqlite_querry)
    records = cursor.fetchall()
    connection.close()
    return records


def db_get_products(id):
    """
    Возвращает продукты по id типов выпечки.
    """
    connection = sqlite3.connect('product_db')
    cursor = connection.cursor()
    sqlite_querry = """
    select * from product where product_type_id = ?"""
    cursor.execute(sqlite_querry, (id,))
    records = cursor.fetchall()
    connection.close()
    return records


def make_proudct_type_keyboard(query):
    """
    Клавиатура для получения товаров.
    """
    count = 0
    keyboard = VkKeyboard(one_time=False)
    for elem in query:
        keyboard.add_callback_button(
            label=f"Показать {elem[1]}",
            color=VkKeyboardColor.POSITIVE,
            payload={"type": f"get_{elem[1]}"},
        )
        count += 1
        if count % 2 == 0:
            keyboard.add_line()
    keyboard.add_callback_button(
            label="Назад",
            color=VkKeyboardColor.NEGATIVE,
            payload={"type": "back_to_menu"},
        )
    return keyboard


def prouduct_message(product):
    """
    Возвращает текстовое сообщение с описанием товара.
    """
    message = (f"Название товара: {product[1]}\n"
               f"Краткое описание: {product[2]}\n")
    return message


def main():
    vk_session = vk_api.VkApi(token=API_GROUP_TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk)

    keyboard_1 = VkKeyboard(one_time=False)
    keyboard_1.add_callback_button(
        label="Показать товары",
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "to_products_type"},
    )

    query = db_get_products_types()
    keyboard_2 = make_proudct_type_keyboard(query)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.obj.message["text"] != "":
                if event.from_user:
                    vk.messages.send(
                        user_id=event.obj.message["from_id"],
                        random_id=get_random_id(),
                        peer_id=event.obj.message["from_id"],
                        keyboard=keyboard_1.get_keyboard(),
                        message=('Добро пожаловать на витрину выпечки!\n'
                                 'Нажав на кнопку в нижней части экрана вы '
                                 'перейдете в каталог наших товаров!')
                    )
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            if event.object.payload.get("type") == "to_products_type":
                vk.messages.send(
                    peer_id=event.object.peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard_2.get_keyboard(),
                    message=('Добро пожаловать в разделы выпечки\n'
                             'Вы можете просмотреть товары нажав на кнопки '
                             'в нижней части экрана.')
                )
            elif event.object.payload.get("type") == "back_to_menu":
                vk.messages.send(
                    peer_id=event.object.peer_id,
                    random_id=get_random_id(),
                    keyboard=keyboard_1.get_keyboard(),
                    message='Добро пожаловать обратно в меню))'
                )
            for elem in query:
                products = db_get_products(elem[0])
                if event.object.payload.get("type") == f"get_{elem[1]}":
                    for product in products:
                        message = prouduct_message(product)
                        img = upload.photo_messages(
                            photos=product[3],
                            peer_id=event.object.peer_id,
                        )
                        owner_id = img[0]['owner_id']
                        photo_id = img[0]['id']
                        access_key = img[0]['access_key']
                        attachment = f'photo{owner_id}_{photo_id}_{access_key}'
                        vk.messages.send(
                            peer_id=event.object.peer_id,
                            random_id=get_random_id(),
                            keyboard=keyboard_2.get_keyboard(),
                            message=message,
                            attachment=attachment
                        )


if __name__ == '__main__':
    cr_sql_db()  # при повторном включении необходимо заккоментировать.
    fill_db()  # при повторном включении необходимо заккоментировать.
    main()
