# uust_oop

Решения лабораторных работ по ООП (УУНиТ).

## Лабораторные работы

Методичка к файлам представлен в [DOC-файле](ООП_лабы_методичка.doc)

| Лабораторная | Тема | Технология |
| --- | --- | --- |
| [Лабораторная 1](lab_1/README.md) | Кнопки и формы | Python, PySide6 |
| [Лабораторная 2](lab_2/README.md) | Объекты и классы | C++20, CMake |
| [Лабораторная 3, часть 1](lab_3_part_1/README.md) | Круги на форме | Python, PySide6 |
| [Лабораторная 3, часть 2](lab_3_part_2/README.md) | MVC | Python, PySide6 |
| [Лабораторная 4](lab_4/README.md) | Визуальный редактор | Python, PySide6 |
| [Лабораторная 5](lab_5/README.md) | Жизненный цикл объектов C++ и виртуальность | C++20, CMake |
| [Лабораторная 6](lab_6/README.md) | Группировка и сохранение | Python, PySide6 |
| [Лабораторная 7](lab_7/README.md) | Дерево объектов, подписка | Python, PySide6 |

## Запуск локально

Для Python-лабораторных нужен PySide6 (можно предварительно создать и использовать виртуальное окружение):

```powershell
pip install -r requirements.txt
python lab_4/main.py
```

Для C++-лабораторных из корня проекта:

```powershell
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

## Автосборка и релизы

Workflow [.github/workflows/release.yml](.github/workflows/release.yml) запускается при публикации тега вида `v*`. Он собирает лабораторные на C++ (2 и 5) через CMake, остальные Python GUI-приложения через PyInstaller, упаковывает архивы для Windows, Linux и macOS x64, затем создает GitHub Release с архивами и `checksums.txt`.
