# 🎬 GuardaSerie Downloader

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-red.svg">
  <img src="https://img.shields.io/github/last-commit/msandy-13/GuardaSerieDownloader.svg">
</p>

**Downloader CLI per guarda-serie.click**
Scarica intere serie in **MP4** direttamente dagli stream HLS *(supervideo.cc + fallback dr0pstream)* usando **yt-dlp**.

---

## ⚠️ Disclaimer

Questo tool è stato creato **solo per scopi educativi e personali**.
L'autore non è responsabile per alcun uso improprio del software.

- Scaricare contenuti protetti da copyright senza autorizzazione può violare le leggi del tuo Paese
- Usa questo script **solo su contenuti di cui possiedi i diritti**
- **Usa a tuo rischio e pericolo**

---

## ✨ Features

- 🎯 Estrazione automatica di tutti gli episodi dalla pagina della serie
- 🔍 Risoluzione dei player offuscati con fallback automatico
- ⚡ Download parallelo configurabile
- 📁 Organizzazione automatica: `downloads / Nome Serie / Stagione X / Episodio.mp4`
- ♻️ Skip automatico dei file già scaricati + resume download interrotti
- 🎛️ Filtro per stagioni, range episodi e qualità
- 📊 Progress bar in tempo reale *(Rich)*
- ⏹️ Premi **Q** per interrompere

---

## 🔧 Come funziona

1. Analizza la pagina della serie su **guarda-serie.click**
2. Estrae i link dei player disponibili per ogni episodio
3. Deoffusca il codice JavaScript per ottenere il link `.m3u8`
4. Usa **yt-dlp** per scaricare e convertire in MP4
5. Organizza i file in cartelle per stagione

Tutto avviene **in locale sul tuo PC**.

---

## 🚀 Installazione

```bash
git clone https://github.com/msandy-13/GuardaSerieDownloader.git
cd GuardaSerieDownloader
pip install -r requirements.txt
```

---

## 📖 Utilizzo

### Comando minimo

```bash
python downloader.py "https://guarda-serie.click/serietv/3176-adventure-time-streaming-ita.html"
```

Con solo l'URL, il downloader:
- Scarica **tutte le stagioni** disponibili
- Usa la **qualità migliore** disponibile
- Salva tutto in `./downloads/Nome Serie/Stagione X/`
- Usa **2 worker** paralleli
- Salta automaticamente i file già presenti

---

## 🎛️ Opzioni

| Opzione | Default | Descrizione |
|---|---|---|
| `--output, -o` | `./downloads` | Cartella dove salvare i file |
| `--quality, -q` | `best` | Qualità video: `best` · `1080` · `720` · `worst` |
| `--workers, -w` | `2` | Numero di download in parallelo |
| `--dry-run` | — | Mostra i link senza scaricare nulla |
| `--st` | — | Scarica solo una stagione specifica (es. `--st 2`) |
| `--ep` | `1` | Episodio iniziale *(usare con `--st`)* |
| `--stop` | fine | Episodio finale *(usare con `--st`)* |
| `--stagioni` | — | Più stagioni con range personalizzati *(vedi sezione dedicata)* |

---

## ⚡ Esempi

```bash
# Tutta la serie (tutte le stagioni)
python downloader.py <URL>

# Solo la stagione 3 completa
python downloader.py <URL> --st 3

# Stagione 2, episodi 5-10
python downloader.py <URL> --st 2 --ep 5 --stop 10

# Qualità 720p con 3 worker
python downloader.py <URL> --quality 720 --workers 3

# Solo anteprima link, nessun download
python downloader.py <URL> --dry-run
```

---

## 📦 Download multi-stagioni

L'opzione `--stagioni` permette di scaricare più stagioni in una volta sola, ognuna con un range di episodi personalizzato.

**Formato:** `"ST EP_INIZIO EP_FINE / ST EP_INIZIO EP_FINE / ..."`

Ogni blocco separato da `/` rappresenta una stagione:

| Parte | Significato |
|---|---|
| `ST` | Numero stagione |
| `EP_INIZIO` | Episodio da cui partire (opzionale, default: 1) |
| `EP_FINE` | Episodio a cui fermarsi (opzionale, default: fine) |

**Esempi:**

```bash
# Stagione 2 completa + stagione 4 completa
python downloader.py <URL> --stagioni "2/4"

# Stagione 2 ep.1-10, stagione 4 ep.3-15
python downloader.py <URL> --stagioni "2 1 10/4 3 15"

# Stagione 1 ep.5 in poi, stagione 3 completa, stagione 5 ep.1-8
python downloader.py <URL> --stagioni "1 5/3/5 1 8"
```

> **Nota:** `--stagioni` e `--st` non si usano insieme. Se usi `--stagioni`, i parametri `--st`, `--ep` e `--stop` vengono ignorati.

---

## 📁 Struttura cartelle

```
downloads/
└── Nome Serie/
    ├── Stagione 1/
    │   ├── 1x01 - Titolo Episodio.mp4
    │   └── 1x02 - Titolo Episodio.mp4
    ├── Stagione 2/
    └── ...
```

---

## 💡 Consigli

- Inizia con `--workers 2` (default) per evitare errori 403
- Non superare **3-4 worker** in parallelo
- Usa `--dry-run` per verificare che tutti gli episodi si risolvano prima di scaricare
- Se un download si interrompe, rilancia lo stesso comando: i file già completati vengono saltati
- Errori 403 frequenti → aspetta qualche minuto e riprova

---

## ❓ Risoluzione problemi

| Problema | Soluzione |
|---|---|
| Nessun episodio trovato | Controlla che l'URL sia corretto |
| m3u8 non trovato | L'episodio potrebbe essere stato rimosso dal sito |
| Errore 403 | Riduci i worker o aspetta prima di riprovare |
| Dipendenze mancanti | `pip install -r requirements.txt` |

---

## 👤 Autore

Creato da **msandy-13** 🇮🇹 — l'ho fatto perché mi serviva, magari serve anche a qualcun altro.

---

## 📄 Licenza

**MIT** — libero uso, modifica e distribuzione.
