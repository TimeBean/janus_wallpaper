import re
import os
import sys

def add_alpha_variants(hex_color: str):
    """
    По 0xRRGGBB возвращает три строки с добавленными альфаканалами
    для прозрачности 90%, 75% и 50% в формате rgba().
    """
    hex_clean = hex_color.lstrip('#')
    if len(hex_clean) != 6 or not re.fullmatch(r'[0-9a-fA-F]{6}', hex_clean):
        raise ValueError(f"Неверный формат цвета: {hex_color}")

    # Преобразуем шестнадцатеричный цвет в компоненты RGB
    r = int(hex_clean[0:2], 16)
    g = int(hex_clean[2:4], 16)
    b = int(hex_clean[4:6], 16)

    variants = []
    for pct, suffix in [(0.90, '90'), (0.75, '75'), (0.50, '50')]:
        # alpha как дробь между 0 и 1
        alpha = pct
        rgba = f"rgba({r}, {g}, {b}, {alpha:.2f})"
        variants.append((suffix, rgba))
    return variants


def process_file(input_path: str):
    # Имя выходного файла: добавляем _opacity перед расширением
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_opacity{ext}"

    # Группируем: 1) весь префикс до имени, 2) само имя, 3) hex-код
    pattern = re.compile(r'^(\s*@define-color\s+)([\w-]+)\s+(#(?:[0-9a-fA-F]{6}));\s*$')

    with open(input_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:

        for line in fin:
            m = pattern.match(line)
            if m:
                define_prefix, name, hexcol = m.group(1), m.group(2), m.group(3)
                # Исходная строка без изменений
                fout.write(line)
                # Три варианта прозрачности в формате rgba()
                for suffix, rgba_col in add_alpha_variants(hexcol):
                    percent = int(float(suffix) / 100 * 100)
                    fout.write(f"{define_prefix}{name}_{suffix} {rgba_col};  /* {percent}% */\n")
            else:
                fout.write(line)

    print(f"Готово: записано в «{output_path}»")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Использование: python add_opacity.py <input_file>")
        sys.exit(1)
    process_file(sys.argv[1])
