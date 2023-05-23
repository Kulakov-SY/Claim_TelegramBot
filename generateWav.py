import asyncio
import shutil

from scipy.io.wavfile import write  # надо устанавливать
import sounddevice as sd
import tts

tts = tts.TTS()


class GenerateWav:
    def create_wav(file_name, example_text):
        global file_to_create
        audio = tts.text_to_wav(example_text, "test-5.wav")
        file_to_create = "wav\\" + str(file_name) + '.wav'
        fs = 1000  # Частота дискретизации
        seconds = 0  # Продолжительность записи
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()  # Дождитесь окончания записи
        write(file_to_create, fs, myrecording)  # Сохранить как WAV файл
        shutil.copyfile(audio, file_to_create)


def create_all(self):

    self.create_wav(file_name='greetings', example_text='Добрый день, уважаемый клиент. Спасибо, '
                                                               'что обратились в компанию «ФЕРО+НИ». Для оперативного рассмотрения Вашей заявки, просьба выслать следующую информацию:')
    self.create_wav(file_name='client_name', example_text='ФИО клиента или наименование партнера:')
    self.create_wav(file_name='client_phone', example_text='Контактный номер телефона клиента или партнера:')
    self.create_wav(file_name='client_city', example_text='Населенный пункт или город, в котором приобреталась дверь:')
    self.create_wav(file_name='client_date', example_text='Дата покупки:')
    self.create_wav(file_name='client_door', example_text='Наименование двери:')
    self.create_wav(file_name='client_description', example_text='Краткое описание выявленного несоответствия:')
    self.create_wav(file_name='client_media', example_text='Добавьте фото или видео лицевой и внутренней стороны дверного блока и выявленного дефекта')
    self.create_wav(file_name='client_force_media', example_text='Для ускорения обработки заявки необходимо добавить фото или видео:')
    self.create_wav(file_name='client_thanks', example_text='Спасибо за обратную связь. В течении двадцати четырех часов с вами свяжется специалист')
    self.create_wav(file_name='client_wrong_data', example_text='Укажите, какие данные неверны')

    print('All audio created')

# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(create_all(self=GenerateWav))
#     loop.close()