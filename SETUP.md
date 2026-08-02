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
winget install --id OpenJS.NodeJS.LTS -e
```

**Зачем каждое:**

- **Git** — версии и синхронизация с Huawei.
- **Python 3.12** — править и проверять `gui_app.py`, `arp_scan.py`.
- **Strawberry Perl** — `latexmk` написан на Perl. Именно его отсутствие дало
  тебе ту ошибку `MiKTeX could not find the script engine 'perl'`. Ставим сразу,
  чтобы не наступать второй раз.
- **MiKTeX** — сам LaTeX.
- **Node.js** — нужен для Claude Code.

**Закрой PowerShell и открой заново** — иначе новые команды не найдутся (в винде
переменная `PATH` подхватывается только новыми окнами).

Проверка, что всё встало:

```powershell
git --version
python --version
perl --version
latexmk --version
node --version
```

Пять строк с версиями — значит готово. Если какая-то команда «не распознана» —
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

**Как этим пользоваться:** заводи отдельный чат под каждую задачу — «Теория:
глава про IPv6», «Автораздача адресов цели», «Корпус и аккумулятор». Контекст
подтянется сам, пересказывать проект заново не придётся.

---

## Часть 7. Claude Code — доступ к малине

Из чата я до Raspberry не дотянусь: моя консоль работает в облаке и твоей
домашней сети не видит. Claude Code запускается в твоём терминале, поэтому видит
всё, что видишь ты — включая малину по SSH.

```powershell
npm install -g @anthropic-ai/claude-code
cd C:\Projects\Bakalarka
claude
```

При первом запуске попросит войти в аккаунт Anthropic.

Он подхватит тот же `CLAUDE.md`, что и я, — контекст общий.

### Ключ вместо пароля

Чтобы не вводить пароль малины каждый раз:

```powershell
ssh-keygen -t ed25519 -C "bakalarka"
ssh-copy-id muk0015@raspberrypi.local
```

Если `ssh-copy-id` не найдётся (в винде его иногда нет):

```powershell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh muk0015@raspberrypi.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

Проверка: `ssh muk0015@raspberrypi.local` должен пустить без пароля.

**Пока не сделаешь ключ — Claude Code до малины не достучится:** он не умеет
вводить пароль в интерактивный запрос SSH.

Если `raspberrypi.local` не резолвится — узнай IP: подключись к тому же хотспоту
и посмотри `arp -a`, потом ходи по IP.

---

## Часть 8. Huawei (Linux)

```bash
sudo pacman -S git texlive-basic texlive-latexextra texlive-bibtexextra \
               texlive-langczechslovak texlive-fontsrecommended biber python
git clone https://github.com/debeeque/Bakalarka_Project.git ~/Bakalarka
```

Дальше в Cowork на Huawei подключаешь папку `~/Bakalarka` — `CLAUDE.md` тот же,
контекст тот же.

**Правило синхронизации:** `git pull` перед началом работы, `git push` после.
Иначе получишь расхождение между ноутами и будешь разбирать конфликты вручную.

Задание (`ThesisSpecification_...pdf`) приедет вместе с репозиторием, когда ты
закоммитишь его на Acer.

---

## Чек-лист

- [ ] Папка переехала в `C:\Projects\Bakalarka`
- [ ] `git`, `python`, `perl`, `latexmk`, `node` отвечают на `--version`
- [ ] MiKTeX Console → install missing packages = **Always**
- [ ] `git push` прошёл, GitHub обновился
- [ ] `ThesisSpecification_...pdf` лежит в корне
- [ ] `latexmk -pdf BachelorThesis.tex` собрал PDF
- [ ] Проект в Claude создан, папка подключена
- [ ] Claude Code запускается
- [ ] SSH-ключ на малине работает без пароля
- [ ] Huawei клонировал репозиторий
