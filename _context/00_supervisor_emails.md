# Переписка с научруком (Ing. Pavel Nevlud)

Извлечено из архива чата Gemini. Полный контекст — `_archive/gemini_bakalarka_export.md`.


## Из хода [4]

```
так давай я тебе обрисую все то что мы делали письмами с моим профессором
```


## Из хода [31]

```
Dobry den,




formát bakalářské práce vypadá v Latexu velmi dobře.

Klíčová část práce je v praktické části, Budete se také muset zaměřit i v praktické části na IPv6 protokol.

Praktická část může obsahovat:

Návrh přenosného zařízení

Realizace generátoru a analyzátoru provozu

Zhodnocení dosažených výsledků







S pozdravem,

Pavel Nevlud вот такой ответ я получил от препода на свое письмо. Расскажичто нам надо сделать или что тебе нужно от меня получить/узнать чтобы расписать наиболее подробно эти важные практические пункты?
```


## Из хода [46]

```
Dobry den,







mam nekolik pripominek k praci:




1. Kapitola 2 - musi byt az za teoretickou casti,  prehodte Kapitolu 2 a Kapitolu 3




2. Obrazek 2.1 - chtelo by to lepe upravit, vypada to dost neusporadane. Mozna by bylo lepsi udelat obrazek jenom analyzatoru/generatoru s USB/LAN adaptery.







S pozdravem,




Pavel Nevlud вот такой вот ответ получил на свою работу, что касается фотки схемы, это я завтра схожу сфоткаю как надо, а пока работаем с тем что имеем. Смотри я хочу сейчас с тобой поговорить на чистоту, ты безусловно хорошая ИИ модель, но в рамках одного чата написания бакаларжки это слишком смело, я хочу чтобы ты помог мне повысить уровень и качество работы путем подключения новых и других сервисов. Например я недавно открыл для себя NotebookLM, с которым даже ты умеешь взаимодействовать, еще я узнал о perplexity и consensus которые идеально подходят для написания текстов, поиска теории и проведению глубоких ресерчей с использованием реальных источников и научной литературы. Я хочу с тобой обсудить что и как можно это подключить к нашей работе. Ты можешь быть типа координатора который будет говорить какую модель и как мне настроить куда какие файлы загрузить какие промты задачи подавать
```


## Из хода [80]

```
Ну ты так пока не торопись, еще работы немало, а пока давай напишем ответное письмо преподу в котором я расскажу что из его требований я выполнил и что обновил. так же расскажу о совсем новом решении с nmap и нумпадом для него, к письму я приложу нынешнюю версию пдф файла. а вот его последнее мне письмо: Dobry den,







mam nekolik pripominek k praci:




1. Kapitola 2 - musi byt az za teoretickou casti,  prehodte Kapitolu 2 a Kapitolu 3




2. Obrazek 2.1 - chtelo by to lepe upravit, vypada to dost neusporadane. Mozna by bylo lepsi udelat obrazek jenom analyzatoru/generatoru s USB/LAN adaptery.







S pozdravem,




Pavel Nevlud







On 3/9/26 00:17, Mikhail Mukanov wrote:Dobrý den,




v příloze Vám zasílám aktualizovanou verzi své bakalářské práce k nahlédnutí.

Na základě Vaší zpětné vazby jsem do praktické části plně integroval podporu protokolu IPv6. Dokument nyní obsahuje i novou sekci se zhodnocením dosažených výsledků z laboratoře, včetně reálných testů propustnosti pro IPv4 i IPv6 a fotografií fungujícího zařízení.

Budu rád za jakékoliv další připomínky.




S pozdravem,

Mikhail Mukanov так же можешь добавить и задать вопросы стоит ли как-то развивать еще в тех плане устройство или этого будет достаточно? там например же есть возможность добавить аккумулятор для автономной работы и тд
```


## Из хода [81]

```
Вот такой вот ответ препода Dobry den,




urcite by bylo vhodne rozsirit prototyp o akumulatorivy modul + vhodnou krabicku do ktere by se vse primontovalo.

Textova cast BP je zatim kratka. BP by mela mit cca 25 stranek od Uvodu po Zaver. 10 stranek teorie + 15 stranek prakticke casti.




Dale se musite rozhodnout, kdy budete statnicovat. Pokud stihnete vse letos, odevzdejte praci letos.

Pokud Vam chybi najaky predmet, je lepsi odevzdat praci az pristi rok a vylepsit ji.




S pozdravem,

Pavel Nevlud
```

---

## Исходящее письмо, 09.09.2026 — перенос на 2027, отчёт за лето, вопрос про 3D-принтер

Отправлено в начале учебного года. Задачи письма: закрепить перенос защиты на
2027 и сохранение темы с тем же научруком, показать летний прогресс, приложить
промежуточный PDF и получить ответ по двум конкретным вопросам про 3D-печать.

Структура выбрана так, чтобы просьба шла **после** отчёта о работе, а не вместо
него, и чтобы отказ по принтеру не блокировал проект — отсюда фраза про
коммерческую печать в конце.

```
Dobrý den,

na začátku nového akademického roku bych Vás rád informoval o stavu
své bakalářské práce.

Podle Vašeho doporučení jsem se rozhodl odevzdat práci až v roce 2027
a využít získaný čas na její vylepšení. Téma bych rád ponechal beze
změny a chtěl bych Vás požádat, zda byste mohl pokračovat ve vedení mé
práce.

Přes léto jsem se věnoval především praktické části:

- Rozšířil jsem zařízení o audit protokolu IPv6: analyzátor zpráv
  Router Advertisement s vyhodnocením příznaků M, O a A, a vyhledávání
  sousedů přes NDP. Vznikly dva nové skripty.

- Vyřešil jsem problém s automatickou konfigurací adres IPv6. Ukázalo
  se, že dnsmasq při stavovém dhcp-range shazoval kromě příznaku M také
  příznak A, čímž znemožnil bezstavovou autokonfiguraci. Řešením bylo
  doplnění klíčového slova slaac. Měřením jsem ověřil, že si cílová
  stanice sestaví globální adresu z prefixu bez jakéhokoli procesu
  v uživatelském prostoru.

- Odstranil jsem chybu, kvůli které Nmap hlásil failed to determine
  route. Sken se spouštěl v nesprávném síťovém jmenném prostoru; nyní
  se jmenný prostor volí podle podsítě cíle. Napevno zapsané adresy
  cílů jsem nahradil jejich automatickým vyhledáním.

- Upravil jsem grafické rozhraní: celoobrazovkový režim a oprava
  vláknové bezpečnosti.

- Textová část má nyní přibližně 8 500 slov a zkušební sazba vychází na
  více než 30 stran od Úvodu po Závěr. Doplnil jsem přílohy o všechny
  zdrojové kódy, vyčistil seznam literatury (14 zdrojů, všechny
  citované v textu) a doplnil sekci Vlastní přínos autora.

V příloze posílám průběžnou verzi práce k nahlédnutí.

Zbývá tedy především to, co jste doporučoval: akumulátorový modul
a krabička.

U napájení jsem vybral UPS modul s články 18650, který podporuje
nabíjení za provozu a měření stavu baterie po sběrnici I2C — zbývající
kapacitu tak bude možné zobrazovat přímo v aplikaci zařízení. Než modul
objednám, chci změřit skutečnou spotřebu zařízení v jednotlivých
režimech, aby byla kapacita zvolena podle naměřených hodnot.

U krabičky jsem zjistil, že běžně prodávané krabičky nevyhovují:
zařízení potřebuje tři konektory RJ45 (integrovaný Ethernet a dva
USB/LAN adaptéry), okno pro pětipalcový displej a prostor pro
akumulátor vedle desek. Chtěl bych proto navrhnout vlastní krabičku
v parametrickém CAD a nechat ji vytisknout na 3D tiskárně.

Rád bych se proto zeptal:

1. Má univerzita 3D tiskárny, které by bylo možné pro tento účel
   využít, případně na koho se mám obrátit?

2. Doporučil byste konkrétní materiál? Uvnitř je Raspberry Pi, které se
   zahřívá, počítám proto spíše s PETG než s PLA.

Pokud tisk na univerzitě možný nebude, zajistím jej komerčně.

Dále mám v plánu pořídit nové snímky obrazovky přímo ze zařízení
(současné jsou vyfocené fotoaparátem), rozšířit panel pro sledování
provozu o statistiky, které poskytnou čísla do kapitoly se zhodnocením
výsledků, a nově vyfotit schéma zapojení, jak jste dříve doporučoval.

Budu rád za jakékoli připomínky.

S pozdravem,
Mikhail Mukanov
```

**Приложение:** промежуточная версия `BachelorThesis.pdf`. Сборка от 04.08.2026
весит 49 МБ и по университетской почте не уходит — отправляется сжатая копия.
Настоящее лечение размера (пересъёмка восьми `gui_*.JPG` через `scrot`,
45 МБ → 0,5 МБ) остаётся в плане и нужно для лимита EDISON в 20 МБ.

**Ожидаемый ответ и что с ним делать:** согласие на перенос и продолжение
руководства; по принтеру — либо контакт лаборатории, либо отказ, после которого
идём в коммерческую печать; возможны новые замечания к тексту.

---

## Входящее письмо, 09.09.2026 (понедельник 12:47) — ответ Nevlud'а

Ответ на письмо от 09.09.2026. Перенос на 2027 и продолжение руководства
возражений не вызвали, обсуждать их он не стал. Два конкретных пункта.

```
Dobry den,

1. Mame na kadedre 3D tiskarny a lze vytisknout pozadovanou krabicku

Kontakt: Ing. Stanislav Hejduk, Ph.D. stanislav.hejduk@vsb.cz

Napiste mu email s odkazem na mne, jako vedouciho BC prace.

S materialem pro tisk se muzete take s nim poradit.

2. Mam pripominku k obrazkum v praci.

Obrazek 3.3 je OK

Obrazky 3.7, 3.8, 3.9 jsou take OK

Obrazky 3.4, 3.5, 3.6, 3.10, 3.11, 3.12, 3.13 a 3.14 by bylo vhodne predelat
jako predchozi obrazky.

Celkove vypada prace celkem pekne. Jsem zvedavy na vyslednou krabicku a napajeni.

S pozdravem,
Pavel Nevlud
```

### Что это значит по пунктам

**3D-печать закрыта.** Кафедра печатает, контакт Ing. Stanislav Hejduk, Ph.D.,
stanislav.hejduk@vsb.cz. Писать самому, со ссылкой на Nevlud'а как научрука,
материал согласовывать с Hejduk'ом. Коммерческая печать больше не нужна.
Блокер «ответ научрука про принтер» из плана снят, остаётся только замер
потребления через INA219.

**Замечание к рисункам полностью совпадает с уже известной проблемой** «фото
экрана вместо скриншота» (пункт 8 плана на лето). Разметка по файлам:

| Рис. | Файл | Что это | Вердикт |
|---|---|---|---|
| 3.3 | `connected_device.JPG` | фото стенда камерой | OK |
| 3.7 | `gui_ra_scan.png` | `scrot`, полноэкранный GUI | OK |
| 3.8 | `gui_neigh_scan.png` | `scrot` | OK |
| 3.9 | `gui_ping_discovered.png` | `scrot` | OK |
| 3.4 | `gui_pingv4.JPG` | фото экрана, 7,2 МБ | переснять |
| 3.5 | `gui_pingv6.JPG` | фото экрана, 6,7 МБ | переснять |
| 3.6 | `gui_arp_scan.JPG` | фото экрана, 4,9 МБ | переснять |
| 3.10 | `gui_speedv4.JPG` | фото экрана, 6,2 МБ | переснять |
| 3.11 | `gui_speedv6.JPG` | фото экрана, 6,5 МБ | переснять |
| 3.12 | `gui_nmap_lan_scan.JPG` | фото экрана, 3,3 МБ | переснять |
| 3.13 | `gui_nmap_wifi_scan.JPG` | фото экрана, 3,3 МБ | переснять |
| 3.14 | `iperf_tests.png` | скриншот терминала на цели | обрезать |

То есть «predelat jako predchozi obrazky» = снять через `scrot` по SSH, в
полноэкранном режиме, без панели LXDE и заголовка окна. Ровно то, что уже
запланировано.

**Рис. 3.14 — отдельный случай.** Это настоящий скриншот, но с окном терминала
на цели: видны заголовок, полоса прокрутки и примерно 40 % пустоты снизу.
Лечится обрезкой до самого текста.

**Рис. 3.1 (`gui.JPG`) и 3.2 (`gui_setup_net.JPG`) он не назвал**, хотя это тоже
фотографии экрана того же происхождения. Скорее всего просмотр, а не решение.
Пересниматься они будут вместе со всеми: оставлять два фото среди девяти
скриншотов бессмысленно, и 7 МБ `gui_setup_net.JPG` всё равно надо убирать
ради лимита EDISON.

**Побочный эффект:** пересъёмка всех восьми `gui_*.JPG` убирает 45 МБ из 47 в
`Figures/`, то есть замечание научрука и лимит EDISON в 20 МБ закрываются одним
действием.

### Что делаем с этим ответом (решено 09.09.2026)

**Ничего не отвечаем прямо сейчас.** Оба пункта требуют сделанной работы, а не
письма.

- **Nevlud'у** пишем, когда будет что показать. Отвечать «хорошо, переделаю»
  смысла нет, работа сдаётся в 2027.
- **Hejduk'у** пишем, когда на руках будут STL-модель и реальные замеры плат.
  Письмо «дайте напечатать что-нибудь» без файла и размеров бессмысленно: он
  всё равно спросит модель, габарит и материал. Порядок: штангенциркуль и
  INA219 → замеры плат и потребления → модель в OpenSCAD → пробники → письмо.
- **Скриншоты не пересснимаем**, пока не закрыт интерфейс (пункт 9 плана,
  метрики в панели сниффинга). Иначе те же кадры придётся снимать дважды. Это
  же было решено 03.08.2026, а фраза «можно делать хоть сейчас» в пункте 8
  плана осталась от более ранней редакции и исправлена.

Когда дойдёт до письма Hejduk'у, в нём должно быть: ссылка на Nevlud'а как
научрука, тема работы одной фразой, габарит корпуса, приложенный STL или STEP,
вопрос про материал (PETG против PLA из-за нагрева Pi), вопрос про допуски на
отверстия под разъёмы и винты и просьба сначала напечатать пробники.
