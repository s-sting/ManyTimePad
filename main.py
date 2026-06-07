import string
import binascii


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


# шифртексты


ciphertexts_hex = []

ciphertexts = [bytes.fromhex(c) for c in ciphertexts_hex]

# XOR всех со всеми


print("=" * 60)
print("XOR ciphertexts")
print("=" * 60)

for i in range(len(ciphertexts)):
    for j in range(i + 1, len(ciphertexts)):
        x = xor_bytes(ciphertexts[i], ciphertexts[j])
        print(f"\nC{i + 1} XOR C{j + 1}")
        for k, b in enumerate(x):
            if 65 <= b <= 90 or 97 <= b <= 122 or 192 <= b <= 255:
                print(f"позиция {k:02d} -> {b:02x} (возможен пробел)")

# поиск пробелов

print("\n" + "=" * 60)
print("ПОИСК ПРОБЕЛОВ")
print("=" * 60)


# Функция проверки, является ли байт русской буквой
def is_russian_letter(b):
    # Русские буквы в cp1251: А-Я = 192-223, а-я = 224-255, Ё=168, ё=184
    return (192 <= b <= 255) or b in [168, 184]


# Функция проверки, может ли байт быть пробелом
def could_be_space(pos, msg_index):
    count = 0
    total = 0

    for j in range(len(ciphertexts)):
        if j == msg_index:
            continue

        if pos < len(ciphertexts[msg_index]) and pos < len(ciphertexts[j]):
            xored = ciphertexts[msg_index][pos] ^ ciphertexts[j][pos]
            if is_russian_letter(xored):
                count += 1
            total += 1

    return count > total // 2


# Находим пробелы для каждого сообщения
space_positions = {}

for i in range(len(ciphertexts)):
    positions = []
    for pos in range(len(ciphertexts[i])):
        if could_be_space(pos, i):
            positions.append(pos)
    space_positions[i] = positions
    print(f"\nСообщение {i + 1}: {len(positions)} пробелов на позициях {positions[:10]}..." if len(
        positions) > 10 else f"\nСообщение {i + 1}: пробелы на {positions}")

# востановление ключа


print("\n" + "=" * 60)
print("ВОССТАНОВЛЕНИЕ КЛЮЧА")
print("=" * 60)

key = {}

for msg_index, positions in space_positions.items():
    ct = ciphertexts[msg_index]
    for pos in positions:
        if pos < len(ct) and pos not in key:
            key[pos] = ct[pos] ^ 0x20  # пробел = 0x20
            print(f"позиция {pos:02d}: key[{pos}] = {key[pos]:02x}")

# Преобразуем ключ в bytes для расшифровки
max_pos = max(key.keys()) if key else 0
key_bytes = bytes(key.get(i, 0) for i in range(max_pos + 1))

# расшифровка


print("\n" + "=" * 60)
print("РАСШИФРОВАННЫЕ СООБЩЕНИЯ (с пропусками)")
print("=" * 60)

for idx, ct in enumerate(ciphertexts):
    result = []
    for pos in range(len(ct)):
        if pos in key:
            decrypted_byte = ct[pos] ^ key[pos]
            try:
                result.append(bytes([decrypted_byte]).decode('cp1251'))
            except:
                result.append('?')
        else:
            result.append('_')

    print(f"\nСообщение {idx + 1}:\n{''.join(result)}")

# полная расшифровка

print("\n" + "=" * 60)
print("РАСШИФРОВАННЫЕ СООБЩЕНИЯ (полный ключ)")
print("=" * 60)

if key_bytes:
    for i, ct in enumerate(ciphertexts, 1):
        # Обрезаем ключ до длины сообщения, если нужно
        key_to_use = key_bytes[:len(ct)]

        # XOR с ключом
        decrypted = bytes(ct[j] ^ key_to_use[j] for j in range(len(ct)))

        # Декодирование
        try:
            text = decrypted.decode("cp1251")
        except UnicodeDecodeError:
            text = decrypted.decode("cp1251", errors="replace")

        print(f"\n{i}: {text}")
else:
    print("Ключ не был восстановлен!")

print("\n" + "-" * 60)
print(f"Длина восстановленного ключа: {len(key_bytes)} байт")
print(f"Всего позиций ключа восстановлено: {len(key)}")
