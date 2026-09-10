# Location CRM Demo

Небольшой локальный прототип CRM для учёта объектов.

## Что есть
- добавление / удаление объектов;
- категории, статусы, примечания;
- строковая координатная метка;
- поиск и фильтр;
- SQLite;
- API `/api/locations`;
- безопасный предпросмотр сообщения и копирование текста;
- синтетическая схема вместо реальной карты.

## Что намеренно отключено
В этой демонстрационной версии нет:
- преобразования реальных MGRS/WGS84;
- поиска ближайших объектов по реальным координатам;
- автоматической отправки точных координат в WhatsApp;
- функций, предназначенных для оперативного наведения или выбора целей.

## Запуск

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

После запуска открыть:

http://127.0.0.1:8000
