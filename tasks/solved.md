# Solved tasks

## weird-rsa (weird-rsa)
- Категория: crypto, beginner
- Флаг: ctfcup{862b7b348272087bd9cc0613646db566}
- Подход: RSA над полиномами GF(257)[x]; N=P*Q факторизован sympy, d=e^-1 mod lcm(p^58-1,p^59-1), m=c^d mod N; коэффициенты m — байты флага (low-first из sage .list()).
- Время: 2026-10-31 ~12:20 MSK

## filter (filter)
- Категория: pwn, beginner
- Флаг: ctfcup{3f3f3558d1484e50275a5e354d7816bd_41c6b450664e2aa3}
- Подход: guard блокирует только соседние байты 0f05/cd80/0f34. Шеллкод XOR-шифруется однобайтовым ключом (подбирается так, чтобы зашифрованный блоб не содержал запрещённых пар), декодер-stub в RWX-памяти расшифровывает тело и выполняет open("/flag.txt")/read/write(1).
- Время: 2026-10-31 ~12:28 MSK

## compuuuter (compuuuter)
- Категория: web, beginner
- Флаг: ctfcup{9cd591ac67dd2dc2b6f439b2c88617be_461e191ef5e661c0}
- Подход: TOCTOU в compute(): guard(type 1337) проверяется один раз в начале, узлы читаются live при вычислении; PATCH меняет тип узла без проверки. Большой граф (20000 узлов), флаговый узел последний, поток переключает тип 1337/1, параллельные compute ловят окно (19 попыток).
- Время: 2026-10-31 ~12:30 MSK

## mmm (mmm)
- Категория: reverse, linux, beginner
- Флаг: ctfcup{99aeaf6c1fb1d156e4194be638825e6f}
- Подход: check() проверяет, что t = M*v (M — 40x40 uint64 в .rodata по 0x3220) пропорционален входу v; у M собственное значение 1337 с рациональным собственным вектором, который и является печатным флагом. hash_check: sha256(вход) == константа по 0x6420. Решено через sympy nullspace (M - 1337*I), проверено обоими условиями.
- Время: 2026-10-31 ~13:05 MSK

## codex (codex)
- Категория: web, http
- Флаг: ctfcup{se3k_and_y3_shall_f1nd_29f0ee273f12f51e}
- Подход: бот (puppeteer) кладёт флаг комментарием admin на page matthew.7 в scope cccccccc-cccc-4ccc-8ccc-cccccccccccc (захардкожен). GET /api/comments не проверяет владельца scope, поэтому по известному UUID список заметок читается без авторизации. Сначала POST /api/visit, чтобы бот записал флаг, затем чтение комментариев.
- Время: 2026-10-31 ~14:03 MSK

## Snake (snake)
- Категория: misc, beginner
- Флаг: ctfcup{23cdba78b236aa2e478d0d562d34562c_cfeb5217f2a27acf}
- Подход: гекс-змейка радиуса 4 (61 клетка), цель = заполнить все клетки (length 61). Еда спавнится случайно в свободной клетке. Найден гамильтонов цикл по 61 клетке (Warnsdorff backtracking); змейка всегда идёт по циклу, тело — непрерывная дуга позади головы, поэтому еда всегда впереди по циклу. Флаг приходит в state.message при победе по WebSocket /ws.
- Время: 2026-10-31 ~12:37 MSK

## my-own-fs (my-own-fs)
- Категория: forensics, filesystem, beginner
- Флаг: ctfcup{dbf75e112fef01db44b2a0e68ab2065e}
- Подход: парсер кастомной ФС из main.rs, удалённый PNG в free inode 2979, флаг отрисован на картинке.
- Время: 2026-10-31 ~12:35 MSK

## mmm (mmm)
- Категория: reverse, linux, beginner
- Флаг: сдан оператором
- Подход: Linux ELF, check(offering) + SHA256 + MATRIX/FLAG_HASH.
- Время: 2026-10-31 ~13:00 MSK

## mmm (mmm)
- Категория: reverse, linux, beginner
- Флаг: сдан оператором (не передал мне)
- Время: 2026-10-31 ~13:00 MSK

## uroki (uroki)
- Категория: web, http
- Флаг: ctfcup{v53_ur0k1_5d3l4ny_5_0gyrc0m_3d0be58212a4d878}
- Подход: (1) `clean_name` не срезает ведущий `/`, поэтому `os.path.join` даёт абсолютный путь и `upload_attachment` пишет файл в произвольное место (в т.ч. `/data/uroki.db`), что даёт произвольное чтение файлов через `file_path` урока и `GET /lesson/<id>/file`. (2) `/flag.txt` chown app + chmod 0000 (entrypoint.sh): читать нельзя, но владелец app может сменить права. (3) RCE от app: celery worker запущен с `-B` в cwd `/data`, beat использует shelve `celerybeat-schedule`; `setup_schedule()` делает `_store.get('tz')`, т.е. unpickle значения ключа `tz`. `dbm.whichdb` проверяет dumb-пару (`<name>.dat` + `<name>.dir`) раньше gdbm-файла, поэтому загрузка двух файлов `/data/celerybeat-schedule.{dat,dir}` с pickle-нагрузкой `eval(...os.system('chmod 644 /flag.txt'))` срабатывает при следующем старте beat. Рестарт celery вызывается созданием урока (`supervisorctl restart celery` в ops.py). Затем подменённая БД с `lessons.id=2 -> /flag.txt`, чтение флага.
- Время: 2026-10-31 ~13:28 MSK
