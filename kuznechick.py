from k_consts import *


def xor(op_a: bytearray, op_b: bytearray) -> bytearray:
    """
    :param op_a: массив байтов 1 для суммы по модулю два
    :param op_b: массив байтов 2 для суммы по модуля два
    :return: возвращает результат побайтового сложения по модулю два
    """
    # определяем место где будем хранить сумму по модулю два
    result = bytearray()
    # проходимся по склеенному массиву из двух предыдуших и ксорим их
    for a, b in zip(op_a, op_b):
        # добавляем это значение в массив байтов результата
        result.append(a ^ b)
    return result


def s_box(data: bytearray) -> bytearray:
    """
    Функция ответственная за Преобразование S на блок схеме
    :param data: на вход подается блок текста 128 бит (16 байт)
    :return: возвращается переставленный текст по таблице S_BOX
    """
    # Коментарии аналогичны следующей функции
    result = bytearray(BLOCK_SIZE)
    for i in range(BLOCK_SIZE):
        result[i] = S_BOX[data[i]]
    return result


def inverse_s_box(data: bytearray) -> bytearray:
    """
    Функция ответственная за преобразование S^-1 на блок схеме
    :param data: на вход подается блок текста 128 бит (16 байт)
    :return: возвращается восстановленный после перестановки текст по таблице S_BOX_REVERSE
    """
    # Определяем массив байтов для результата длиной в BLOCK_SIZE = 16 байт (128 бит)
    result = bytearray(BLOCK_SIZE)
    for i in range(BLOCK_SIZE):
        """
        В таблице S_BOX_REVERSE 256 значений (байт всегда меньше 255, включая 0 получаются все индексы таблицы), 
        мы берем значение очередного байта из последовательности, ищем элемент таблицы под этим номером и значение 
        этого элемента и будет значением очередного нового байта в преобразованной последовательности. 
        """
        result[i] = S_BOX_REVERSE[data[i]]
    return result


def r_box(data: bytearray) -> bytearray:
    """
    Функция ответственная за преобразование R, находится внутри преобразования L в блок-схеме
    :param data: на вход подается блок текста 128 бит (16 байт)
    :return: преобразованный блок текста 128 бит (16 байт)
    """
    # Тут происходит магия Галуа и сдвиг регистра (я их сам до конца не понял хых)
    first_element = 0
    result = bytearray(BLOCK_SIZE)
    for i in range(BLOCK_SIZE):
        result[i] = data[i - 1]
        first_element = first_element ^ GF[i][result[i]]
    result[0] = first_element
    return result


def inverse_r_box(data: bytearray) -> bytearray:
    last_element = 0
    result = bytearray(BLOCK_SIZE)
    for i in range(BLOCK_SIZE - 1, -1, -1):
        result[i - 1] = data[i]
        last_element = last_element ^ GF[i][data[i]]
    result[15] = last_element
    return result


def l_box(data: bytearray) -> bytearray:
    """
    Функция ответственная за L преобразование на блок-схеме
    :param data: на вход подается блок текста 128 бит (16 байт)
    :return: преобразованный блок текста 128 бит (16 байт)
    """
    result = data
    # Просто повторяем 16 раз преобразование R
    for _ in range(16):
        result = r_box(result)
    return result


def inverse_l_box(data: bytearray) -> bytearray:
    result = data
    # Просто повторяем 16 раз преобразование R
    for _ in range(16):
        result = inverse_r_box(result)
    return result


def generate_iter_c():
    """
    В данном шифре 10 раундов, для каждого из раундов нужен свой ключ, ключи генерируются из исходного с помощью
    коэффицентов, которые можно вычеслить и записать в память но удобнее их сгенерировать
    :return: Массив коэффицентов для каждой итерации генерации ключей
    """
    # Определяем пустой массив в который будем запихивать наши коэффиценты
    iter_c = []
    for i in range(1, 33):
        # Создаем массив байтов длиной в блок текста (потому что нам понадобится его запихнуть в L преобразование)
        internal = bytearray(BLOCK_SIZE)
        # Назначаем нашему последнему байту значение итерации (из него получается значение константы)
        internal[15] = i
        # Производим L преобразование над нашим байтом
        iter_c.append(l_box(internal))
    return iter_c


def f_key(key_n: bytearray, c_i: bytearray):
    """
    Функция F используемая в генерации ключей
    :param key_n: предыдущая половина ключа, подающаяся на вход функции
    :param c_i: итерационная константа
    :return: преобразованная половинка ключа
    """
    # Сначала ксорим ключ с итерационной константой
    xored = xor(key_n, c_i)
    # Производим сначала S преобразование, а затем и L преобразование и наконец возвращаем нашу половинку
    return l_box(s_box(xored))


def generate_round_keys(init_key: bytearray):
    """
    Функция выработки 10 ключей из исходного ключа
    :param init_key: ключ задаваемый пользователем
    :return: массив из 10 ключей для каждого раунда шифрования
    """
    # Получаем наши константы
    cs = generate_iter_c()
    # Бьем ключ на половинки
    k_1 = init_key[:KEY_SIZE // 2]
    k_2 = init_key[KEY_SIZE // 2:]
    # Создаем массив ключиков и заисываем в него наши исходные половинки, они и будут первым и вторым ключиком
    generated_keys = [k_1, k_2]
    # Фактически нужно ещё 8 ключей
    for i in range(4):
        """
        Для получения каждой пары ключей нам нужно прогнать k1 через F, заксорить что получили F с k2
        и приравнять k1 к результату этого, а значение k2 приравнять к значению k1 на прошлом ходе ровно 8 раз
        """
        for j in range(8):
            # Приравниваем k_1 к ксору k_2 и функции F от k_1 и итерационного ключа (соответствуеющего итерации)
            # k_2 приравниваем к значению k_1 до этого безобразия
            k_1, k_2 = [xor(k_2, f_key(k_1, cs[i * 8 + j])), k_1]
        # Добавляем это безобразие в массив сгенерированных ключей
        generated_keys.append(k_1)
        generated_keys.append(k_2)
    return generated_keys


# Самое сложное позади

def encrypt(block: bytearray, keys: list[bytearray]):
    """
    Функция для шифрования
    :param block: очерездной 16-байтовый блок текста
    :param keys: сгенерированные ключи
    :return: зашифрованный блок текста
    """
    # Сначала шифровка равна исходному тексту
    cypher = block
    # Потом мы ксорим его с соответствующим ключом производим S преобразование и L преобразование 9 раз
    for i in range(9):
        cypher = xor(cypher, keys[i])
        cypher = s_box(cypher)
        cypher = l_box(cypher)
    # На последок мы его ещё раз заксорим
    cypher = xor(cypher, keys[9])
    return cypher


# Она не понадобилась хых
def decrypt(block: bytearray, keys: list[bytearray]):
    """
    Фуеция для расшифрования
    :param block: очередной блок шифротекста
    :param keys: сгенерированные ключи
    :return: расшифрованыый блок тектса
    """
    # Сначала расшифровка равна шифровке
    decryption = block
    # Для начала мы её заксорим ибо напоследок мы тоже ксорили
    decryption = xor(decryption, keys[9])
    # 9 раз подряд производим операции, обратные операциям при шифровании в обратном порядке
    for i in range(8, -1, -1):
        decryption = inverse_l_box(decryption)
        decryption = inverse_s_box(decryption)
        decryption = xor(decryption, keys[i])
    return decryption
