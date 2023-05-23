import queue
import shutil
import smtplib
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, InputFile
import aiogram.utils.markdown as md
from aiogram.types import ParseMode
import owncloud
import logging
import os
from pathlib import Path
from aiogram import Bot, Dispatcher, executor, types

from w2n import make_num_versions
from stt import STT
from tts import TTS

logging.basicConfig(level=logging.INFO)  # Устанавливает конфигурацию логирования на уровне INFO.
API_TOKEN = 'YOUR_TOKEN_HERE'  # Задает переменную API_TOKEN со значением токена API. Здесь нужно заменить 'YOUR_TOKEN_HERE' на реальный токен API.
bot = Bot(token=API_TOKEN)  # Создает экземпляр бота с использованием токена API.
stt = STT()  # Создает экземпляр объекта STT (Speech-to-Text).
tts = TTS()  # Создает экземпляр объекта TTS (Text-to-Speech).
storage = MemoryStorage()  # Создает экземпляр объекта хранилища памяти.
dp = Dispatcher(bot, storage=storage)  # Создает экземпляр диспетчера с использованием бота и хранилища.

global list_media  # Объявляет глобальную переменную list_media.
list_media = []  # Инициализирует переменную list_media пустым списком.
control = 0  # Инициализирует переменную control значением 0.
q = queue.Queue()  # Создает экземпляр очереди.
oc = owncloud.Client('CLOUD.CLIENT',
                     verify_certs=False)  # Создает экземпляр клиента ownCloud с указанным URL-адресом и отключенной проверкой сертификата.
oc.login('LOGIN', 'PASS')  # Выполняет вход в систему ownCloud с заданными учетными данными.


# States

class Form(StatesGroup):  # Определяет класс Form для работы со стейтами.
    def __init__(self):  # Конструктор класса Form.
        self.list_media = []  # Инициализирует переменную list_media пустым списком.


nameClient = State()  # Определяет состояние nameClient.
phone = State()  # Определяет состояние phone.
city = State()  # Определяет состояние city.
datas = State()  # Определяет состояние datas.
model = State()  # Определяет состояние model.
description = State()  # Определяет состояние description.
media = State()  # Определяет состояние media.
final = State()  # Определяет состояние final.
remark = State()  # Определяет состояние remark.
link_list = State()  # Определяет состояние link_list.
user_id = State()  # Определяет состояние user_id.


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.nameClient.set()  # Устанавливает текущее состояние на nameClient.
    voice_start = InputFile("wav/greetings.wav")  # Задает файл с голосовым приветствием.
    await bot.send_voice(message.from_user.id, voice_start,
                         caption="Добрый день, уважаемый клиент. Спасибо, что обратились в компанию». Для оперативного " \
                                 "рассмотрения Вашей заявки, просьба выслать следующую информацию: ",
                         reply_markup=ReplyKeyboardRemove())  # Отправляет голосовое сообщение с приветствием.
    try:
        oc.mkdir(f'{message.from_user.id}_{message.from_user.first_name}_{message.from_user.last_name}')
        # Создает папку на сервере ownCloud с идентификатором пользователя в качестве имени папки.
    except:
        print('папка уже существует')  # Выводит сообщение, если папка уже существует.

    text_fio = "ФИО клиента или наименование партнера:"  # Задает текстовое сообщение.
    voice_fio = InputFile("wav/client_name.wav")  # Задает файл с голосовым сообщением.
    await bot.send_voice(message.from_user.id, voice_fio, caption=text_fio, reply_markup=ReplyKeyboardRemove())
    # Отправляет голосовое сообщение с запросом ФИО клиента или наименования партнера.


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()  # Получает текущее состояние.
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)  # Выводит информацию о текущем состоянии.
    await state.finish()  # Завершает работу со стейтами.
    await message.reply('Отменено.',
                        reply_markup=types.ReplyKeyboardRemove())  # Отправляет ответное сообщение "Отменено".


@dp.message_handler(state=Form.nameClient, content_types=types.ContentTypes.ANY)
async def nameClient(message: types.Message, state: FSMContext):
    if message.text != '/start':  # Проверка, что сообщение не является командой '/start'
        if message.text:  # Проверка, что сообщение содержит текст
            if control == 0:  # Проверка значения переменной 'control'
                async with state.proxy() as data:  # Асинхронный доступ к данным состояния
                    data['nameClient'] = message.text  # Запись текста сообщения в поле 'nameClient' в состоянии
                    data['first_name'] = message.from_user.first_name  # Запись имени отправителя сообщения в поле 'first_name' в состоянии
                    data['last_name'] = message.from_user.last_name  # Запись фамилии отправителя сообщения в поле 'last_name' в состоянии
                    data['user_id'] = message.from_user.id  # Запись идентификатора пользователя в поле 'user_id' в состоянии
                    data['video_count'] = 0  # Инициализация счетчика видео в состоянии
                    data['photo_count'] = 0  # Инициализация счетчика фотографий в состоянии
                    data['audio_count'] = 0  # Инициализация счетчика аудиофайлов в состоянии
                await Form.next()  # Переход к следующему шагу формы

                text_phone = "Контактный номер телефона клиента или партнера:"  # Текст сообщения с запросом номера телефона
                voice_phone = InputFile("wav/client_phone.wav")  # Загрузка аудиофайла с записью запроса номера телефона
                await bot.send_voice(message.from_user.id, voice_phone, caption=text_phone,
                                     reply_markup=ReplyKeyboardRemove())  # Отправка аудиосообщения с запросом номера телефона

            else:
                async with state.proxy() as data:  # Асинхронный доступ к данным состояния
                    data['nameClient'] = message.text  # Запись текста сообщения в поле 'nameClient' в состоянии
                await media(message, state)  # Вызов функции 'media' для обработки медиафайлов
                await all_info(message, state)  # Вызов функции 'all_info' для обработки всей информации

        elif message.voice:  # Проверка, что сообщение является голосовым сообщением
            text = await stt_audio(message)  # Преобразование голосового сообщения в текст

            if control == 0:  # Проверка значения переменной 'control'
                async with state.proxy() as data:  # Асинхронный доступ к данным состояния
                    data['nameClient'] = text  # Запись преобразованного текста в поле 'nameClient' в состоянии
                    data['first_name'] = message.from_user.first_name  # Запись имени отправителя сообщения в поле 'first_name' в состоянии
                    data['last_name'] = message.from_user.last_name  # Запись фамилии отправителя сообщения в поле 'last_name' в состоянии
                    data['user_id'] = message.from_user.id  # Запись идентификатора пользователя в поле 'user_id' в состоянии
                    data['video_count'] = 0  # Инициализация счетчика видео в состоянии
                    data['photo_count'] = 0  # Инициализация счетчика фотографий в состоянии
                    data['audio_count'] = 0  # Инициализация счетчика аудиофайлов в состоянии
                await Form.next()  # Переход к следующему шагу формы

                text_phone = "Контактный номер телефона клиента или партнера:"  # Текст сообщения с запросом номера телефона
                voice_phone = InputFile("wav/client_phone.wav")  # Загрузка аудиофайла с записью запроса номера телефона
                await bot.send_voice(message.from_user.id, voice_phone, caption=text_phone,
                                     reply_markup=ReplyKeyboardRemove())  # Отправка аудиосообщения с запросом номера телефона

            else:
                async with state.proxy() as data:  # Асинхронный доступ к данным состояния
                    data['nameClient'] = text  # Запись преобразованного текста в поле 'nameClient' в состоянии
                await media(message, state)  # Вызов функции 'media' для обработки медиафайлов
                await all_info(message, state)  # Вызов функции 'all_info' для обработки всей информации

        else:
            voice_fio = InputFile("wav/client_name.wav")  # Загрузка аудиофайла с записью запроса фамилии, имени и отчества/наименования партнера
            await bot.send_voice(message.from_user.id, voice_fio,
                                 caption="Назовите фамилию имя отчество/наименование партнера",
                                 reply_markup=ReplyKeyboardRemove())  # Отправка аудиосообщения с запросом фамилии, имени и отчества/наименования партнера
            return

    else:
        await cmd_start(message)  # Вызов функции 'cmd_start' для обработки команды '/start'

@dp.message_handler(state=Form.phone, content_types=types.ContentTypes.ANY)
async def phone(message: types.Message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if control == 0:
                async with state.proxy() as data:
                    data['phone'] = message.text

                await Form.next()
                voice_city = InputFile("wav/client_city.wav")
                await bot.send_voice(message.from_user.id, voice_city,
                                     caption="Населенный пункт/город, в котором приобретался продукт:",
                                     reply_markup=ReplyKeyboardRemove())
            else:
                async with state.proxy() as data:
                    data['phone'] = message.text
                await media(message, state)
                await all_info(message, state)

        elif message.voice:
            text = await stt_audio(message)

            list_number = make_num_versions(text)
            for item in list_number:
                if len(item) == 11:
                    text = item

            if control == 0:
                async with state.proxy() as data:
                    data['phone'] = text

                await Form.next()
                voice_city = InputFile("wav/client_city.wav")
                await bot.send_voice(message.from_user.id, voice_city,
                                     caption="Населенный пункт/город, в котором приобретался продукт:",
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['phone'] = text
                await media(message, state)
                await all_info(message, state)

        else:
            voice_phone = InputFile("wav/client_phone.wav")
            await bot.send_voice(message.from_user.id, voice_phone,
                                 caption="Контактный номер телефона клиента/партнера:",
                                 reply_markup=ReplyKeyboardRemove())
            return
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.city, content_types=types.ContentTypes.ANY)
async def city(message: types.Message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if control == 0:
                async with state.proxy() as data:
                    data['city'] = message.text

                await Form.next()

                text_date = "Дата покупки:"
                voice_date = InputFile("wav/client_date.wav")
                await bot.send_voice(message.from_user.id, voice_date, caption=text_date,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['city'] = message.text
                await media(message, state)
                await all_info(message, state)

        elif message.voice:
            text = await stt_audio(message)

            if control == 0:
                async with state.proxy() as data:
                    data['city'] = text
                await Form.next()

                text_date = "Дата покупки:"

                voice_date = InputFile("wav/client_date.wav")
                await bot.send_voice(message.from_user.id, voice_date, caption=text_date,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['city'] = text
                await media(message, state)
                await all_info(message, state)

        else:
            voice_city = InputFile("wav/client_city.wav")
            await bot.send_voice(message.from_user.id, voice_city,
                                 caption="Населенный пункт/город, в котором приобретался продукт:",
                                 reply_markup=ReplyKeyboardRemove())
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.datas, content_types=types.ContentTypes.ANY)
async def datas(message: types.Message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if control == 0:
                async with state.proxy() as data:
                    data['datas'] = message.text

                await Form.next()

                text_model = "Наименование продукта:"
                voice_model = InputFile("wav/client_product.wav")
                await bot.send_voice(message.from_user.id, voice_model, caption=text_model,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['datas'] = message.text
                await media(message, state)
                await all_info(message, state)

        elif message.voice:
            text = await stt_audio(message)

            if control == 0:
                async with state.proxy() as data:
                    data['datas'] = text
                await Form.next()

                text_model = "Наименование продукта:"
                voice_model = InputFile("wav/client_product.wav")
                await bot.send_voice(message.from_user.id, voice_model, caption=text_model,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['datas'] = text
                await media(message, state)
                await all_info(message, state)

        else:
            text_date = "Дата покупки:"
            voice_date = InputFile("wav/client_date.wav")
            await bot.send_voice(message.from_user.id, voice_date, caption=text_date,
                                 reply_markup=ReplyKeyboardRemove())
            return
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.model, content_types=types.ContentTypes.ANY)
async def model(message: types.Message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if control == 0:
                async with state.proxy() as data:
                    data['model'] = message.text

                await Form.next()

                text_description = "Краткое описание выявленного несоответствия:"
                voice_description = InputFile("wav/client_description.wav")
                await bot.send_voice(message.from_user.id, voice_description, caption=text_description,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['model'] = message.text
                await media(message, state)
                await all_info(message, state)

        elif message.voice:
            text = await stt_audio(message)

            if control == 0:
                async with state.proxy() as data:
                    data['model'] = text

                await Form.next()

                text_description = "Краткое описание выявленного несоответствия:"
                voice_description = InputFile("wav/client_description.wav")
                await bot.send_voice(message.from_user.id, voice_description, caption=text_description,
                                     reply_markup=ReplyKeyboardRemove())

            else:
                async with state.proxy() as data:
                    data['model'] = text
                await media(message, state)
                await all_info(message, state)

        else:
            text_model = "Наименование продукта:"
            voice_model = InputFile("wav/client_product.wav")
            await bot.send_voice(message.from_user.id, voice_model, caption=text_model,
                                 reply_markup=ReplyKeyboardRemove())

            return
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.description, content_types=types.ContentTypes.ANY)
async def description(message: types.Message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if control == 0:
                async with state.proxy() as data:
                    data['description'] = message.text

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add("Нажмите сюда, если все фото и видео добавлены")

                voice_media = InputFile("wav/client_media.wav")
                await bot.send_voice(message.from_user.id, voice_media,
                                     caption="Добавьте фото или видео лицевой и внутренней стороны продукта и выявленного дефекта",
                                     reply_markup=markup)
                await Form.media.set()
            else:
                async with state.proxy() as data:
                    data['description'] = message.text
                await media(message, state)
                await all_info(message, state)

        elif message.voice:
            text = await stt_audio(message)

            if control == 0:
                async with state.proxy() as data:
                    data['description'] = text

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add("Нажмите сюда, если все фото и видео добавлены")

                voice_media = InputFile("wav/client_media.wav")
                await bot.send_voice(message.from_user.id, voice_media,
                                     caption="Добавьте фото или видео лицевой и внутренней стороны продукта и выявленного дефекта",
                                     reply_markup=markup)

                await Form.media.set()
            else:
                async with state.proxy() as data:
                    data['description'] = text
                await media(message, state)
                await all_info(message, state)


        else:
            text_description = "Краткое описание выявленного несоответствия:"
            voice_description = InputFile("wav/client_description.wav")
            await bot.send_voice(message.from_user.id, voice_description, caption=text_description,
                                 reply_markup=ReplyKeyboardRemove())
            return
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.media, content_types=types.ContentTypes.ANY)
async def media(message, state: FSMContext):
    async with state.proxy() as data:
        if message.text != '/start':
            first_name = data['first_name']
            last_name = data['last_name']
            dir_to_create = f'{message.from_user.id}_{first_name}_{last_name}'

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Нажмите сюда, если все фото и видео добавлены")
            try:
                if message.text is None:
                    if message.photo:
                        file_info = await bot.get_file(message.photo[-1].file_id)
                        src = dir_to_create + '/' + file_info.file_path
                        list_media.append(src)
                        await message.photo[-1].download(destination_dir=dir_to_create + '/')

                        oc.put_file(dir_to_create + '/', src)
                        link_info_photo = oc.share_file_with_link(dir_to_create + '/')

                        async with state.proxy() as data:
                            data['link_list'] = link_info_photo.get_link()
                            data['photo_count'] = data['photo_count'] + 1

                    elif message.video:
                        file_info = await bot.get_file(message.video.file_id)
                        src = dir_to_create + '/' + file_info.file_path
                        list_media.append(src)
                        await message.video.download(destination_dir=dir_to_create + '/')

                        oc.put_file(dir_to_create + '/', src)
                        link_info_video = oc.share_file_with_link(dir_to_create + '/')

                        async with state.proxy() as data:
                            data['link_list'] = link_info_video.get_link()
                            data['video_count'] = data['video_count'] + 1

                    elif message.audio:
                        file_info = await bot.get_file(message.audio[-1].file_id)
                        src = dir_to_create + '/' + file_info.file_path
                        list_media.append(src)
                        await message.audio[-1].download(destination_dir=dir_to_create + '/')

                        oc.put_file(dir_to_create + '/', src)
                        link_info_audio = oc.share_file_with_link(dir_to_create + '/')

                        async with state.proxy() as data:
                            data['link_list'] = link_info_audio.get_link()
                            data['audio_count'] = data['audio_count'] + 1

                elif message.text == "Нажмите сюда, если все фото и видео добавлены":
                    if len(list_media) > 0:
                        await all_info(message, state)
                    else:

                        text_need_description = "Для ускорения обработки заявки необходимо добавить фото или видео:"
                        voice_need_description = InputFile("wav/client_force_media.wav")
                        await bot.send_voice(message.from_user.id, voice_need_description,
                                             caption=text_need_description,
                                             reply_markup=markup)
                    return
                else:

                    text_need_media = "Добавьте фото или видео"
                    voice_need_media = InputFile("wav/client_force_media.wav")
                    await bot.send_voice(message.from_user.id, voice_need_media, caption=text_need_media,
                                         reply_markup=markup)
            except:
                print("Что-то пошло не так с медиа...")
        else:
            await cmd_start(message)


async def all_info(message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=True)
    markup.add("ДА")
    markup.add("НЕТ")

    async with state.proxy() as data:
        await bot.send_message(

            message.from_user.id,
            md.text(
                md.text('Все данные верны?'),
                md.text('ФИО клиента/Наименование партера: ', data['nameClient']),
                md.text('Контактный номер телефона клиента/партнера: ', data['phone']),
                md.text('Населенный пункт/город, в котором приобреталась продукт: ', data['city']),
                md.text('Дата покупки: ', data['datas']),
                md.text('Наименование продукта: ', data['model']),
                md.text('Краткое описание выявленного несоответствия: ', data['description']),
                md.text('Добавлено: фото -', data['photo_count'], ',видео - ', data['video_count']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    await Form.final.set()


@dp.message_handler(state=Form.final, content_types=types.ContentTypes.ANY)
async def get_final(message, state: FSMContext):
    if message.text != '/start':
        if message.text:
            if message.text.find("ДА" or "Да" or "да") != -1:
                voice_yes = InputFile("wav/client_thanks.wav")
                await bot.send_voice(message.from_user.id, voice_yes, caption="Спасибо за обратную связь. В течении "
                                                                              "двадцати четырех часов с вами свяжется"
                                                                              " специалист",
                                     reply_markup=ReplyKeyboardRemove())
                try:
                    await send_email(state)
                    await state.finish()
                    global control
                    control = 0
                    shutil.rmtree(
                        f'{message.from_user.id}_{message.from_user.first_name}_{message.from_user.last_name}')
                    list_media.clear()
                except:
                    print("Что-то пошло не так с отправкой")

            elif message.text.find("НЕТ" or "НЕт" or "Нет" or "нЕт" or "нЕТ" or "неТ") != -1:
                btn1 = types.KeyboardButton("ФИО клиента/ Наименование партера")
                btn2 = types.KeyboardButton("Контактный номер телефона клиента/партнера")
                btn3 = types.KeyboardButton("Населенный пункт/город, в котором приобретался продукт")
                btn4 = types.KeyboardButton("Дата покупки")
                btn5 = types.KeyboardButton("Наименование продукта")
                btn6 = types.KeyboardButton("Краткое описание выявленного несоответствия")
                btn7 = types.KeyboardButton("Добавить новые фото/видео")
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btn1).add(btn2).add(
                    btn3).add(btn4).add(btn5).add(btn6).add(btn7)

                text_no = "Укажите, какие данные неверны"
                voice_no = InputFile("wav/client_wrong_data.wav")
                await bot.send_voice(message.from_user.id, voice_no, caption=text_no,
                                     reply_markup=markup)

                await Form.remark.set()
            else:
                await all_info(message, state)
            return
    else:
        await cmd_start(message)


@dp.message_handler(state=Form.remark, content_types=types.ContentTypes.ANY)
async def get_remark(message, state: FSMContext):
    if message.text != '/start':
        global control
        control = 1
        if message.text:
            if message.text == "ФИО клиента/ Наименование партера":
                await bot.send_message(message.from_user.id, 'Введите исправленные ФИО клиента/ Наименование партера',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.nameClient.set()

            elif message.text == "Контактный номер телефона клиента/партнера":
                await bot.send_message(message.from_user.id,
                                       'Введите исправленные контактный номер телефона клиента/партнера',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.phone.set()

            elif message.text == "Населенный пункт/город, в котором приобреталась продукт":
                await bot.send_message(message.from_user.id,
                                       'Введите исправленные населенный пункт/город, в котором приобреталась продукт',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.city.set()

            elif message.text == "Дата покупки":
                await bot.send_message(message.from_user.id, 'Введите исправленную дату покупки',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.datas.set()

            elif message.text == "Наименование продукта":
                await bot.send_message(message.from_user.id, 'Введите исправленное наименование продукта',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.model.set()

            elif message.text == "Краткое описание выявленного несоответствия":
                await bot.send_message(message.from_user.id,
                                       'Введите исправленное краткое описание выявленного несоответствия',
                                       reply_markup=ReplyKeyboardRemove())
                await Form.description.set()

            elif message.text == "Добавить новые фото/видео":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
                markup.add("Нажмите сюда, если все фото и видео добавлены")
                await bot.send_message(message.from_user.id,
                                       'Добавьте фото/видео', reply_markup=markup)
                await Form.media.set()

        else:
            await all_info(message, state)
            return
    else:
        await cmd_start(message)


async def send_email(state: FSMContext):
    async with state.proxy() as data:
        print(data)

        nameClient = str('ФИО клиента/ Наименование партнера: ' + data['nameClient'])
        phone = 'Контактный номер телефона клиента/партнера: ' + data['phone']
        city = 'Населенный пункт/город, в котором приобретался продукт: ' + data['city']
        datas = 'Дата покупки: ' + data['datas']
        model = 'Наименование продукта: ' + data['model']
        description = 'Краткое описание выявленного несоответствия: ' + data['description']
        id_user = 'ID пользователя OwnCloud: ' + str(data['user_id'])
        if len(data['link_list']) > 0:
            media = 'Медиа файлы от клиента: ' + data['link_list']
        else:
            media = 'Отсутствуют'

        subject = f"Претензия от {data['first_name']} {data['last_name']}"  # Тема сообщения
        to = "YOUR_MAIL"  # Получатель
        sender = "bot@YOUR_MAIL.ru"  # Адресат
        smtpserver = smtplib.SMTP("SERVER_ADDRESS", 587) # Адрес сервера и порт
        user = 'LOGIN' #Имя юзера отправителя
        password = 'PASS' #Пасс юзера отправителя
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(user, password)
        header = 'Адресат:' + to + '\n' + 'Получатель: ' + sender + '\n' + 'Тема:' + subject + '\n\n'
        info_mail = header + nameClient + "\n" + phone + "\n" + city + "\n" + datas + "\n" + model + "\n" + description + "\n" + media + "\n" + id_user
        message = header + f'\n {info_mail}'
        smtpserver.sendmail(sender, to, message.encode("utf8"))
        smtpserver.close()


async def stt_audio(message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)
    text = stt.audio_to_text(file_on_disk)
    try:
        os.remove(file_on_disk)  # Удаление временного файла
    except:
        print('файла нет')
    return text


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cmd_start())
    loop.close()
