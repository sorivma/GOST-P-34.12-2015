"""
ФАЙЛ ИСПОЛЬЗУЕМЫЙ ДЛЯ ОТЛАДКИ МНОЙ МОЖЕШЬ УДАЛИТЬ ЕГО
"""
from main import *

byte_s_1 = [
    0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00
]


# Пройден
def test_s():
    print("S")
    s_1 = s_box(bytearray(byte_s_1))
    print(s_1.hex().upper())
    s_2 = s_box(bytearray(s_1))
    print(s_2.hex().upper())
    s_3 = s_box(bytearray(s_2))
    print(s_3.hex().upper())
    s_4 = s_box(bytearray(s_3))
    print(s_4.hex().upper())
    r_s_3 = inverse_s_box(s_4)
    r_s_2 = inverse_s_box(r_s_3)
    r_s_1 = inverse_s_box(r_s_2)
    print(r_s_1 == s_1)
    print(r_s_2 == s_2)
    print(r_s_3 == s_3)


test_s()

byte_r = [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00
]

print("===============================================")


def test_r():
    print("R")
    r_1 = r_box(bytearray(byte_r))
    print(r_1.hex().upper())
    r_2 = r_box(bytearray(r_1))
    print(r_2.hex().upper())
    r_3 = r_box(bytearray(r_2))
    print(r_3.hex().upper())
    r_4 = r_box(bytearray(r_3))
    print(r_4.hex().upper())
    r_r_3 = inverse_r_box(r_4)
    r_r_2 = inverse_r_box(r_r_3)
    r_r_1 = inverse_r_box(r_r_2)
    print(r_r_1 == r_1)
    print(r_r_2 == r_2)
    print(r_r_3 == r_3)


test_r()

byte_l = [
    0x64, 0xa5, 0x94, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]

print("===============================================")


def test_l():
    print("L")
    l_1 = l_box(bytearray(byte_l))
    print(l_1.hex().upper())
    l_2 = l_box(bytearray(l_1))
    print(l_2.hex().upper())
    l_3 = l_box(bytearray(l_2))
    print(l_3.hex().upper())
    l_4 = l_box(bytearray(l_3))
    print(l_4.hex().upper())
    r_l_3 = inverse_l_box(l_4)
    print(r_l_3.hex().upper())
    r_l_2 = inverse_l_box(r_l_3)
    print(r_l_2.hex().upper())
    r_l_1 = inverse_l_box(r_l_2)
    print(r_l_1.hex().upper())
    print(r_l_1 == l_1)
    print(r_l_2 == l_2)
    print(r_l_3 == l_3)


test_l()

print("================================================")

for iter_c in generate_iter_c():
    print(iter_c.hex().upper())

print("================================================")

key_b = [
    0x88, 0x99, 0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0xfe, 0xdc, 0xba,
    0x98, 0x76, 0x54, 0x32, 0x10, 0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef
]

key_c = [
    0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00, 0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88, 0xef, 0xcd, 0xab,
    0x89, 0x67, 0x45, 0x23, 0x01, 0x10, 0x32, 0x54, 0x76, 0x98, 0xba, 0xdc, 0xfe
]

keys = generate_round_keys(bytearray(key_b))
for key in keys:
    print(key.hex().upper())

print("=====================================")

open_text = [
    0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x00, 0xff, 0xee, 0xdd, 0xcc, 0xbb, 0xaa, 0x99, 0x88
]

enc = encrypt(bytearray(open_text), keys)
print(enc.hex().upper())
print("----------------")
print(decrypt(enc, keys).hex().upper())

print("====================================")

print((1).to_bytes(8, "big").hex().upper())
string = "Забор"
byte_string = bytearray(string.encode())
print(byte_string.hex().upper())
blocks = splt_str_on_blocks("Однонаправленная функция - одно из ключевых понятий в современной криптографии", 16)

for block in blocks:
    print(block.hex().upper())

print("====================================")
print("GAMMA")
