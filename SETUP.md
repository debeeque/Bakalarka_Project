# Настройка рабочего места

Одноразовый гайд. Прошёл его — забыл. Дальше живём в `CLAUDE.md`.

Два компьютера:

| | Acer (Windows 11) | Huawei (Linux) |
|---|---|---|
| Роль | 90% работы: текст, код, сборка PDF | лаборатория, тесты с устройством |
| Что ставим | MiKTeX, Perl, Git, Python, VS Code, Claude Code | git, texlive, python — через пакетный менеджер |
| Синхронизация | ← GitHub `Bakalarka_Project` → | |

---

## Часть 0. Что решено и почему

**WSL не ставим.** Ты просил «не сложно, не жрёт ресурсов, мало места», а у тебя
40 ГБ свободных. WSL — это виртуальная машина: свой диск, который только растёт,
свой кусок RAM, и постоянная путаница «я сейчас в винде или в линуксе, и почему
путь выглядит не так». За это платят, когда нужен именно линукс. Тебе не нужен:
всё линуксовое живёт на малине и на Huawei.

Плюс у MiKTeX есть свойство, которое здесь решает: он **докачивает недостающие
пакеты сам** в момент компиляции. Твоей работе нужны `pdfx`, `biblatex`,
`babel-czech`, `listings`, `pdfpages`, `titlesec` — я проверил по `diploma.cls`.
На линуксовом TeX Live за них пришлось бы ставить `texlive-full` — это 7 ГБ.
MiKTeX возьмёт ~1 ГБ и дотянет остальное по мере надобности.

Итого ~2,5 ГБ вместо ~10 ГБ.

**Папка проекта: `C:\Projects\Bakalarka`.** Короткий путь, без пробелов и скобок.
`Documents\Bakalarka (claude)` — рабочее название на время переноса; пробел и
скобки в пути регулярно ломают LaTeX и заставляют экранировать всё в терминале.

**Синхронизация между ноутами: git.** Репозиторий уже есть, оба ноута клонируют
его. Никакого Dropbox: LaTeX генерирует десятки временных файлов, облачные
синхронизаторы на них сходят с ума и плодят конфликты.

**Проект один, не два.** Каждая новая функция устройства сразу требует абзаца в
практической части — разделять их значит постоянно пересказывать одно другому.

---

## Часть 1. Переносим папку

Открой PowerShell (Win → набери `powershell` → Enter) и выполни:

```powershell
mkdir C:\Projects
Move-Item "C:\Users\Debeeque\Documents\Bakalarka (claude)" C:\Projects\Bakalarka
```

Проверь, что доехало:

```powershell
dir C:\Projects\Bakalarka
```

Должны быть: `CLAUDE.md`, `BachelorThesis.tex`, `Chapters`, `Figures`,
`SourceCodes`, `_context`, `_archive`.

---

## Часть 2. Ставим инструменты

Всё ставится через `winget` — это встроенный в Windows 11 пакетный менеджер,
ближайший родственник `pacman`. Одна команда в PowerShell:

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id StrawberryPerl.StrawberryPerl -e
winget install --id MiKTeX.MiKTeX -e
```

**Зачем каждое:**

- **Git** — версии и синхронизация с Huawei.
- **Python 3.12** — править и проверять `gui_app.py`, `arp_scan.py`.
- **Strawberry Perl** — `latexmk` написан на Perl. Именно его отсутствие дало
  тебе ту ошибку `MiKTeX could not find the script engine 'perl'`. Ставим сразу,
  чтобы не наступать второй раз.
- **MiKTeX** — сам LaTeX.

**Закрой PowerShell и открой заново** — иначе новые команды не найдутся (в винде
переменная `PATH` подхватывается только новыми окнами).

Проверка, что всё встало:

```powershell
git --version
python --version
perl --version
latexmk --version
```

Четыре строки с версиями — значит готово. Если какая-то команда «не распознана» —
скажи мне какая, разберёмся.

### Настройка MiKTeX

Запусти **MiKTeX Console** (Win → `MiKTeX Console`) → вкладка **Settings** →
пункт *«You want to install missing packages»* поставь в **Always**.

Без этого он будет останавливать сборку и спрашивать разрешение на каждый
недостающий пакет — а их при первой компиляции будет много.

Там же на вкладке **Updates** нажми *Check for updates* и обнови.

---

## Часть 3. Возвращаем git

Сейчас в папке лежат файлы без истории — я скопировал рабочее дерево, потому что
склонировать напрямую в подключённую папку у меня не вышло. Восстанавливаем связь
с GitHub:

Сначала представься git — на свежей винде он тебя не знает:

```powershell
git config --global user.name "debeeque"
git config --global user.email "skala123458@gmail.com"
```

Затем:

```powershell
cd C:\Projects\Bakalarka
git init
git remote add origin https://github.com/debeeque/Bakalarka_Project.git
git fetch origin
git branch -m main
git reset origin/main
git add -A
git status
```

**Что тут происходит по шагам:**

1. `git init` — делает папку репозиторием (создаёт скрытую `.git`).
2. `git remote add origin ...` — говорит «твой сервер вот здесь».
3. `git fetch origin` — качает историю с GitHub, файлы не трогает.
4. `git branch -m main` — переименовывает локальную ветку в `main`.
   `git init` в винде создаёт ветку `master`, а на GitHub твоя ветка называется
   `main` — если не переименовать, push уедет не туда.
5. `git reset origin/main` — подставляет историю под твои файлы. **Рабочие файлы
   не трогает** (их стирает только `--hard`, его тут нет). Теперь git видит
   разницу между мартовской версией и текущей.
6. `git status` — покажет, что изменилось.

Ожидаемо увидишь: новые `CLAUDE.md`, `SETUP.md`, `_context/`, `_archive/`;
удалённые `coffee.bib`, `BachelorThesis.bbl-SAVE-ERROR`,
`SourceCodes/ArraySortingAlgorithms.cpp`, `Figures/CoffeeAndComputer.jpg` — это
мусор из шаблона, я его вычистил.

Фиксируем и отправляем:

```powershell
git commit -m "Перенос проекта в Claude: контекст, архив чата, чистка шаблона"
git push origin main
```

Если `git push` попросит логин — он откроет окно браузера для входа в GitHub.

### Про перевод строк

При `git add` посыпались предупреждения `LF will be replaced by CRLF`. Windows
и Linux помечают конец строки по-разному, и git по умолчанию подставляет
виндовый вариант. Для `.tex` это безобидно, но `setup_network.sh` уезжает на
малину — а bash на виндовых переводах строк падает с
`bad interpreter: /bin/bash^M`. Ошибка выглядит необъяснимо, ищется долго.

Поэтому в корне лежит `.gitattributes`: он заставляет git хранить `.sh`, `.py`
и `.tex` всегда в линуксовом формате. Файл уже создан, ничего делать не нужно —
просто не удаляй его.

---

## Часть 4. Кладём задание на место

**Это обязательно, иначе работа не соберётся.**

Я нашёл неприятное: `diploma.cls` вшивает PDF с заданием прямо в работу
(`\includepdf[pages=-]{ThesisSpecification_...}`), а в `.gitignore` стояло
`*.pdf` — то есть файл никогда не попадал в репозиторий. У тебя он был локально,
поэтому проблема не всплывала. После переустановки винды его нет.

Скачай из Drive:
https://drive.google.com/file/d/1PIxTeAjZAmXRSsxc24-XZktCfB73AKAM/view

и положи в `C:\Projects\Bakalarka\` под именем
`ThesisSpecification_MUK0015_vsboee250462E0.pdf` (имя должно совпасть точно —
оно прописано в `BachelorThesis.tex`).

В `.gitignore` я уже добавил для него исключение, так что в этот раз он
закоммитится.

---

## Часть 5. Первая сборка

```powershell
cd C:\Projects\Bakalarka
latexmk -pdf BachelorThesis.tex
```

Первый раз пойдёт долго — MiKTeX будет докачивать пакеты. Дальше секунды.

Результат — `BachelorThesis.pdf` в той же папке.

Убрать временный мусор: `latexmk -c`

### VS Code

```powershell
code --install-extension James-Yu.latex-workshop
code --install-extension ms-python.python
```

Открой папку: `code C:\Projects\Bakalarka`

LaTeX Workshop сам подхватит `latexmk` и будет пересобирать PDF при сохранении,
с предпросмотром рядом.

---

## Часть 6. Проект в Claude

1. В боковой панели → **Projects** → **New project**
2. Название: **Бакалаврская — Portable Network Analyzer**
3. Описание: `Přenosné zařízení pro testování a monitorování sítí. VŠB-TUO, сдача 2027. Устройство на Raspberry Pi + текст работы в LaTeX.`
4. Подключи папку **C:\Projects\Bakalarka**

Загружать файлы в «знания» проекта не нужно — папка подключена, я читаю её
напрямую, и `CLAUDE.md` подхватывается автоматически в начале каждого чата.

### Три поля справа — что куда

- **Context** → папка `Bakalarka`. Главное поле. Отсюда я читаю `CLAUDE.md`,
  главы, код. Уже настроено.
- **Instructions** → короткая памятка на случай, когда чат идёт в режиме
  **Chat** (без доступа к файлам) — тогда `CLAUDE.md` не читается и правила
  разговора теряются. Впиши туда:

  > Отвечай только по-русски. Работа пишется на академическом чешском —
  > сплошной текст, без буллетов внутри глав, без канцелярита. Ссылаться на ИИ
  > как на источник нельзя: всё заимствованное требует реального источника в
  > библиографии. Подробный контекст — в файле CLAUDE.md в папке проекта.

- **Memory** → не трогай. Всё, что должно пережить чаты, живёт в `CLAUDE.md`,
  и это лучше: файл лежит в git, едет на Huawei, виден Claude Code.

**Как этим пользоваться:** заводи отдельный чат под каждую задачу — «Теория:
глава про IPv6», «Автораздача адресов цели», «Корпус и аккумулятор». Контекст
подтянется сам, пересказывать проект заново не придётся.

---

## Часть 7. Claude Code — доступ к малине

Из обычного чата до Raspberry не дотянуться: та консоль работает в облаке и
домашнюю сеть не видит. Нужен Claude Code — он выполняется **на твоей машине**,
поэтому видит всё, что видишь ты, включая малину по SSH.

**Ставить ничего не надо.** В десктопном приложении вверху слева есть вкладка
**Code** — это он и есть. Никакого `npm install`.

1. Открой вкладку **Code**
2. Внизу выбери папку — укажи `C:\Projects\Bakalarka`
3. Убедись, что режим стоит **Local** (а не удалённый) — именно локальный режим
   даёт доступ к твоей сети
4. Пиши задачу обычным текстом

Он подхватит тот же `CLAUDE.md`, что и чат, — контекст общий.

**Когда что использовать:**

| | Обычный чат (вкладка Home) | Claude Code (вкладка Code) |
|---|---|---|
| Текст работы, главы, литература | да | можно, но незачем |
| Правка кода в `SourceCodes/` | да | да |
| SSH на малину, запуск скриптов там | **нет** | **да** |
| Долгие серии команд, отладка | неудобно | да |

### Ключ вместо пароля

**Пока не сделаешь ключ — Claude Code до малины не достучится:** он не умеет
вводить пароль в интерактивный запрос SSH, тот просто повиснет.

Малина должна быть **включена и в той же сети**, что ноутбук (хотспот с
телефона), иначе шаг 2 не пройдёт.

#### 0. Проверить, что SSH-клиент есть

```powershell
ssh -V
```

В Windows 11 OpenSSH встроен. Если команда не найдена:
`winget install --id Microsoft.OpenSSH.Beta -e`

#### 1. Создать пару ключей

```powershell
ssh-keygen -t ed25519 -C "bakalarka"
```

Он спросит три вещи:

- **путь к файлу** — жми Enter, дефолт подходит
  (`C:\Users\Debeeque\.ssh\id_ed25519`)
- **passphrase** — жми Enter, оставь **пустым**
- **повтор passphrase** — снова Enter

Пустой пароль на ключе — сознательный выбор. С паролем каждый вызов SSH будет
требовать ввода, и Claude Code упрётся ровно в ту же стену, ради обхода которой
всё это и делается. Обойти можно через `ssh-agent`, но это лишний слой ради
доступа к лабораторной малине в домашней сети. Если ноутбук потеряешь —
достаточно будет удалить ключ из `authorized_keys` на устройстве.

Появятся два файла: `id_ed25519` (**приватный, никому и никогда**) и
`id_ed25519.pub` (публичный, его и раздают).

#### 2. Положить публичный ключ на малину

```powershell
$key = Get-Content "$env:USERPROFILE\.ssh\id_ed25519.pub"
ssh muk0015@raspberrypi.local "mkdir -p ~/.ssh && chmod 700 ~/.ssh && echo '$key' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Это последний раз, когда потребуется ввести пароль от малины.

`chmod` в конце обязателен: SSH молча игнорирует `authorized_keys`, если права
на файл или папку слишком широкие. Это самая частая причина «ключ положил, а всё
равно спрашивает пароль».

В винде нет `ssh-copy-id`, поэтому команда выглядит так громоздко. Ключ
передаётся одной строкой через переменную — если пропустить её через `type` или
`Get-Content` конвейером, PowerShell добавит виндовые переводы строк и ключ на
малине окажется битым.

#### 3. Короткое имя вместо длинного адреса

Создай файл `C:\Users\Debeeque\.ssh\config` (без расширения) с содержимым:

```
Host malina
    HostName raspberrypi.local
    User muk0015
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 30
```

Теперь вместо `ssh muk0015@raspberrypi.local` достаточно `ssh malina`.
`ServerAliveInterval` не даёт сессии отваливаться на долгих операциях вроде
сканов Nmap.

Если малина окажется по IP, а не по имени — правишь одну строку `HostName`
в этом файле, и всё остальное продолжает работать.

#### 4. Проверить

```powershell
ssh malina
```

Должен пустить сразу, без пароля. Внутри — `exit` для выхода.

#### Если не пустило

- **`Could not resolve hostname raspberrypi.local`** — mDNS не отработал.
  Узнай IP: на малине `hostname -I`, либо с ноутбука `arp -a` (ищи адрес из
  подсети хотспота). Подставь IP в `HostName` в `.ssh\config`.
- **Всё ещё спрашивает пароль** — почти всегда права. Зайди по паролю и проверь:
  `ls -ld ~/.ssh ~/.ssh/authorized_keys` — должно быть `drwx------` и `-rw-------`.
- **`Permission denied (publickey)`** — ключ не доехал. Посмотри
  `cat ~/.ssh/authorized_keys` на малине: там должна быть одна строка,
  начинающаяся с `ssh-ed25519` и заканчивающаяся на `bakalarka`.

---

## Часть 8. Huawei (Arch Linux)

### 1. Пакеты

```bash
sudo pacman -S --needed git python biber \
    texlive-basic texlive-latex texlive-latexrecommended texlive-latexextra \
    texlive-bibtexextra texlive-fontsrecommended texlive-langczechslovak \
    texlive-binextra
```

Что за что отвечает:

| Пакет | Зачем именно нам |
|---|---|
| `texlive-binextra` | **`latexmk`** — он живёт здесь, а не в `texlive-basic` |
| `texlive-latexextra` | `pdfx` (PDF/A), `pdfpages`, `titlesec`, `subfig`, `tocbibind`, `xmpincl` |
| `texlive-latexrecommended` | `csquotes`, `listings` |
| `texlive-bibtexextra` | `biblatex` и стиль `biblatex-iso690` |
| `texlive-langczechslovak` | `babel-czech` — чешские переносы и типографика |
| `texlive-fontsrecommended` | Latin Modern, требуемый регламентом шрифт |
| `biber` | обработчик библиографии, отдельный пакет |

На Arch TeX Live разбит на части, и `latexmk` в `texlive-binextra` — это самая
частая причина «поставил texlive, а latexmk не находится».

Проверка: `latexmk --version && biber --version && git --version`

### 2. Репозиторий

```bash
git config --global user.name "debeeque"
git config --global user.email "skala123458@gmail.com"

git clone https://github.com/debeeque/Bakalarka_Project.git ~/Bakalarka
cd ~/Bakalarka
latexmk -pdf BachelorThesis.tex
```

`git config` нужен по той же причине, что и на Acer, — без него первый же
коммит упрётся в «Author identity unknown».

Задание и логотип приедут вместе с репозиторием — они закоммичены.

### 3. Ключ на малину

В лаборатории ты подключаешься к устройству именно с Huawei, поэтому ключ нужен
и здесь. На Linux всё короче, чем в винде:

```bash
ssh-keygen -t ed25519 -C "bakalarka-huawei"     # три раза Enter
ssh-copy-id muk0015@raspberrypi.local
```

`ssh-copy-id` на Linux есть из коробки, городить конструкцию с переменной, как
в PowerShell, не нужно.

Тот же короткий алиас — создай `~/.ssh/config`:

```
Host malina
    HostName raspberrypi.local
    User muk0015
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 30
```

```bash
chmod 600 ~/.ssh/config
ssh malina
```

Ключи у ноутбуков **разные, и это правильно** — каждый со своим. Потеряешь один
ноутбук, удалишь одну строку из `authorized_keys`, второй продолжит работать.

### 4. Подключить папку

В Cowork на Huawei подключаешь `~/Bakalarka` — `CLAUDE.md` тот же, контекст тот
же, начинать заново ничего не нужно.

### Правило синхронизации

`git pull` перед началом работы, `git push` после. Всегда, на обоих ноутбуках.
Иначе получишь расхождение и будешь разбирать конфликты руками — на LaTeX это
особенно неприятно.

---

## Чек-лист

**Acer (Windows 11)**

- [x] Папка переехала в `C:\Projects\Bakalarka`
- [x] `git`, `python`, `perl`, `latexmk` отвечают на `--version`
- [x] MiKTeX Console → install missing packages = **Always**
- [x] `git push` прошёл, GitHub обновился
- [x] `ThesisSpecification_...pdf` и `Figures/FEI_CZ.pdf` на месте
- [x] `latexmk -pdf BachelorThesis.tex` собрал PDF, формат **A4** проверен
- [x] Проект в Claude создан, папка подключена
- [x] SSH-ключ на малине работает без пароля
- [ ] Поле **Instructions** в проекте заполнено (Часть 6)

**Huawei (Arch)**

- [x] `git config` с именем и почтой
- [x] Репозиторий склонирован в `~/Bakalarka`
- [x] SSH-ключ на малине работает, алиас `ssh malina`
- [x] Папка `~/Bakalarka` подключена в Claude
- [x] ~~TeX Live~~ — не нужен, пока не понадобится собирать PDF в лаборатории
- [x] ~~mDNS~~ — разобрано, упирается в домашний роутер, не чинится со стороны
  ноутбука. В `~/.ssh/config` прописан IP; в лаборатории проверить
  `getent hosts raspberrypi.local` и, если ответит, заменить на имя.
- [ ] Huawei клонировал репозиторий
