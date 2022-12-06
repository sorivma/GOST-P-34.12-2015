from kuznechick import *
from k_consts import *

# Его знают под многими именами (IV, initialization vector, вектор инициализации, синхропосылка, но значения его байтов
# могут быть любыми (от 0 до 255) и смысл в том чтобы сгенерированные псевдослучайные значения отличались от друг-друга
# при разных сеансах свяхи
IV = bytearray([
    0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88
])


def splt_str_on_blocks(in_string: str, block_size: int, encoding: str) -> list[bytearray]:
    """
    В этой функции происходит форменная магия, мы разбиваем строку на блоки заданной, попутно преобразуя их в массивы
    байтов определенной длины в указанной кодировке. Если же на блоки одинаковой длины массив байтов не бъется:
    Пример 129 байтов а разбить надо на блоки по 64 он разобьет строку на три массива байтов длинами 64,64 и 1 байт
    :param in_string: входящая строка
    :param block_size: размер блока
    :param encoding: кодировка
    :return: массив массивов байтов (список наших блоков тектса к примеру)
    """
    # Переводим строку в кодировку (byte-string)
    encoded_str = in_string.encode(encoding)
    # Бъем byte-string на кусочки равной длины
    chunks = [encoded_str[i:i + block_size] for i in range(0, len(encoded_str), block_size)]
    # Переводим byte-string в массив байтов (да-да в питоне byte-string и bytearray разные вещички!
    # (byte-string неизменяем))
    blocks = [bytearray(chunk) for chunk in chunks]
    return blocks


def gam(blocks: list[bytearray], key: str) -> list[bytearray]:
    """
    Функция для нашего гаммирования
    :param blocks: блоки нашего текста в байтах
    :param key: строка ключа
    :return: блоки шифротекста
    """
    # Тут придумана хитрость, ключ делится на блоки фактически равные своей длине, если ключ введенный пользователем в
    # байтах оказался длиннее, то лишнее выскочит в другой блок, в то время как мы берем только первый. Таким финтом
    # ушами убивается сразу два зайца - перевести строку в байты и обрезать её если она слишком длинная.
    byte_key = splt_str_on_blocks(key, KEY_SIZE, "UTF-8")[0]
    # А здесь обслуживается уже другой вариант, когда наш ключ недостаточно длинный, мы просто будем добавлять нули,
    # пока ключ не станет нужной длины
    while len(byte_key) != KEY_SIZE:
        byte_key.append(0)
    # Получаем сгенерированные ключи из ключа пользователя
    generated_keys = generate_round_keys(byte_key)
    # Наш счётчик, который будет отвечать за изменение блока гаммы для каждого последующего блока шифротекста/открытого
    # текста
    counter = 0
    # Массив для хранения блоков шифротекста/открытого тектса
    output = []
    # Идём по блокам сообщения
    for block in blocks:
        # Шифру мы должны передать конкатенированные вектор инициализации и счётчик, но вот незадача, вход в наш шифр
        # имеет размер 16 байт, а наш IV всего-лишь 8 байт, а counter вообще integer. Есть идея. Питон позволяет
        # перевести integer в byte-string, с заданным количеством байт (нам нужно 8), а этот byte-string мы с легкостью
        # можем перевести в bytearray и сконкатенировать с нашим IV. В сумме как раз получается 16 байт. но есть одна
        # проблема вдруг у нас counter примет значение больше чем может вместить в себя 8 байт. В таком случае мы
        # бессильны и наша программа вылетит с ошибкой. НО. данный вариант маловероятен ибо в консоль просто так такое
        # огромное количество символов написать просто невозможно. (4294967295 - значение счётчика, не символов,
        # счётчик увеличивается только с каждым новым блоком текста в одном блоке текста около 16 символов, что в свою
        # очередь даёт нам лимит в 4294967295*16 = 68719476720 почти 69 миллиардов символов Карл!!!!)
        iv_i = IV + bytearray(counter.to_bytes(8, "big"))
        # Наконец-то вырабатываем гамму для очередного блока текста
        gamma = encrypt(iv_i, generated_keys)
        # Ксорим гамму и блок текста
        xored_block = xor(gamma, block)
        # Добавляем к остальным блокам
        output.append(xored_block)
        # Увеличиваем счётчик для следующего блока шифра
        counter += 1
    return output


def build_str_out_of_encoding(blocks: list[bytearray], encoding: str) -> str:
    """
    Функция для создания текста из блоков массивов байтов
    :param blocks: список блоков текста (массивы байтов)
    :param encoding: кодировка в которой мы хотим получить нашу строку
    :return: наша строка
    """
    # Сначала для избежания ошибок нам очень бы хотелось запихнуть всё в один bytearray
    msg_bytes = bytearray()
    # Делаем это
    for block in blocks:
        msg_bytes += block
    # Возвращаем декодированный массив байтов через заданную нами кодировку
    return msg_bytes.decode(encoding)


# Просим пользователя ввести своё сообщение
user_message = input("Введите сообщение: ")
# Так же просим ввести его ключ
user_key = input("Введите ключ: ")
# Преобразуем наш текст в блоки из массивов байтов (в кодировке UTF-8 потому что нам в неё ещё и расшифровывать потом)
byte_message = splt_str_on_blocks(user_message, BLOCK_SIZE, "UTF-8")
# Получаем шифровку
encryption = gam(byte_message, user_key)
# Выводим шифровку (т.к. при шифровке у нас выходит месиво из байтов ни один уважающий себя кодек не декодирует это
# во что-либо и вылетит с ошибкой, к счастью для нас существуют такие что совсем себя не уважают)
print("Зашифрованное сообщение: " + build_str_out_of_encoding(encryption, "latin-1"))
# Вспоминаем что это гаммирование и функция расшифровки нам и не нужна (используем ту же что и для шифрования)
decryption = gam(encryption, user_key)
# Выводим данное расшифрованное сообщение в человеческой кодировке
print("Расшифрованное сообщение: " + build_str_out_of_encoding(decryption, "UTF-8"))
