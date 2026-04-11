# 🎬 GuardaSerie Downloader

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20Linux-red.svg">
  <img src="https://img.shields.io/github/last-commit/msandy-13/GuardaSerieDownloader.svg">
</p>

**Downloader CLI per guarda-serie.click**
>Scarica intere serie in **MP4** direttamente dagli stream HLS usando **yt-dlp**.
Supporta **vixsrc.to** (Player1), **supervideo.cc** (Player2) e **dr0pstream.com** (Player3) con fallback automatico.

![Demo](https://github.com/msandy-13/GuardaSerieDownloader/blob/main/asset/demo.png)

---

## ⚠️ Disclaimer

Questo tool è stato creato **solo per scopi educativi e personali**.
Non sono responsabile per alcun uso improprio del software.

- Scaricare contenuti protetti da copyright senza autorizzazione può violare le leggi del tuo Paese
- Usa questo script **solo su contenuti di cui possiedi i diritti**
- **Usa a tuo rischio e pericolo**

---

## ✨ Features

- 🎯 Estrazione automatica di tutti gli episodi dalla pagina della serie
- 🔀 Fallback automatico tra player: **vixsrc → supervideo → dr0pstream**
- 🇮🇹 Preferenza automatica della traccia audio **italiana** quando disponibile
- ♻️ **Retry automatico** (3 tentativi) con token m3u8 fresco ad ogni tentativo
- ⚡ Download parallelo configurabile
- 📁 Organizzazione automatica: `Downloads / Nome Serie / Stagione X / S01E01 - Titolo.mp4`
- ⏭️ Skip automatico dei file già scaricati + resume download interrotti
- 🎛️ Filtro per stagioni, range episodi, episodi specifici e qualità
- 📦 **Batch download** da file `.txt` con più serie
- 📊 Progress bar in tempo reale con schermo pulito *(Rich)*
- ⏹️ Premi **Q** per interrompere istantaneamente
- 🐧 Compatibile con **Windows** e **Linux/Ubuntu Server**

---

## 🔧 Come funziona

1. Analizza la pagina della serie su **guarda-serie.click**
2. Estrae tutti i player disponibili per ogni episodio (`data-link`)
3. Per ogni player, risolve il link di streaming:
   - **vixsrc.to** → legge `window.masterPlaylist` dall'HTML
   - **supervideo / dr0pstream** → deoffusca il JS `eval()` per estrarre il token m3u8
4. Al momento del download, prende un **token fresco** (evita scadenze)
5. Usa **yt-dlp** per scaricare video + audio italiano e unirli in MP4
6. Organizza i file in cartelle per stagione

Tutto avviene **in locale sul tuo PC**.

---

## 🚀 Installazione

```bash
git clone https://github.com/msandy-13/GuardaSerieDownloader.git
cd GuardaSerieDownloader
pip install -r requirements.txt
```

> Su **Ubuntu/Linux** usa un virtualenv per evitare conflitti col sistema:
> ```bash
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> ```

---

## 📖 Utilizzo

### Comando minimo

```bash
python downloader.py "https://guarda-serie.click/serietv/3176-adventure-time-streaming-ita.html"
```

Con solo l'URL, il downloader:
- Scarica **tutte le stagioni** disponibili
- Usa la **qualità migliore** con **audio italiano** se disponibile
- Salva tutto in `./Downloads/Nome Serie/Stagione X/`
- Usa **2 worker** paralleli
- Salta automaticamente i file già presenti

---

## 🎛️ Opzioni

| Opzione | Default | Descrizione |
|---|---|---|
| `--output, -o` | `./Downloads` | Cartella dove salvare i file |
| `--quality, -q` | `best` | Qualità video: `best` · `1080` · `720` · `worst` |
| `--workers, -w` | `2` | Numero di download in parallelo |
| `--dry-run` | — | Mostra i link senza scaricare nulla |
| `--st` | — | Scarica solo una stagione specifica (es. `--st 2`) |
| `--ep` | `1` | Episodio iniziale *(usare con `--st`)* |
| `--stop` | fine | Episodio finale *(usare con `--st`)* |
| `--episodes` | — | Episodi specifici non contigui (es. `--episodes 3,7,12`) |
| `--stagioni` | — | Più stagioni con range personalizzati *(vedi sezione dedicata)* |
| `--batch` | — | URL è un file `.txt` con una serie per riga |

---

## ⚡ Esempi

```bash
# Tutta la serie (tutte le stagioni)
python downloader.py <URL>

# Solo la stagione 3 completa
python downloader.py <URL> --st 3

# Stagione 2, episodi 5-10
python downloader.py <URL> --st 2 --ep 5 --stop 10

# Episodio singolo
python downloader.py <URL> --st 1 --ep 7 --stop 7

# Episodi specifici non contigui
python downloader.py <URL> --st 1 --episodes 3,7,12,15

# Qualità 720p con 3 worker
python downloader.py <URL> --quality 720 --workers 3

# Solo anteprima link, nessun download
python downloader.py <URL> --dry-run

# Batch download da file
python downloader.py URLs.txt --batch
```

---

## 📦 Download multi-stagioni

L'opzione `--stagioni` permette di scaricare più stagioni in una volta sola, ognuna con un range di episodi personalizzato.

**Formato:** `"ST EP_INIZIO EP_FINE / ST EP_INIZIO EP_FINE / ..."`

```bash
# Stagione 2 completa + stagione 4 completa
python downloader.py <URL> --stagioni "2/4"

# Stagione 2 ep.1-10, stagione 4 ep.3-15
python downloader.py <URL> --stagioni "2 1 10/4 3 15"

# Stagione 1 ep.5 in poi, stagione 3 completa, stagione 5 ep.1-8
python downloader.py <URL> --stagioni "1 5/3/5 1 8"
```

> **Nota:** `--stagioni` e `--st` non si usano insieme.

---

## 📦 Batch download

Crea un file `URLs.txt` con una serie per riga:

```
https://guarda-serie.click/serietv/3176-adventure-time-streaming-ita.html
https://guarda-serie.click/serietv/1719-smallville-streaming-ita.html
# Le righe che iniziano con # sono ignorate
```

Poi lancia:

```bash
python downloader.py URLs.txt --batch
```

---

## 📁 Struttura cartelle

```
Downloads/
└── Nome Serie/
    ├── Stagione 1/
    │   ├── S01E01 - Titolo Episodio.mp4
    │   ├── S01E02 - Titolo Episodio.mp4
    │   └── ...
    ├── Stagione 2/
    └── ...
```

Il formato `S01E01` è compatibile con **Plex**, **Jellyfin** e tutti i principali media player.

---

## 🔁 Retry automatico

Se un download fallisce (token scaduto, errore di rete, CDN irraggiungibile):

1. Prende un **token m3u8 fresco** dal server
2. Riprova fino a **3 volte** automaticamente
3. Se tutti i tentativi falliscono, prova il **player successivo** (fallback)
4. Se tutti i player falliscono, segna l'episodio come fallito e continua

---

## 🔀 Player di fallback

Il downloader prova automaticamente i player nell'ordine in cui appaiono sulla pagina:

| Player | Dominio | Metodo estrazione |
|---|---|---|
| Player1 | `vixsrc.to` | `window.masterPlaylist` |
| Player2 | `supervideo.cc` | Deoffuscazione `eval()` JS |
| Player3 | `dr0pstream.com` | Deoffuscazione `eval()` JS |

Se il sito aggiunge nuovi player compatibili, vengono rilevati automaticamente.

---

## 💡 Consigli

- Inizia con `--workers 2` (default) per evitare errori 403
- Non superare **3 worker** in parallelo
- Usa `--dry-run` per verificare che tutti gli episodi si risolvano prima di scaricare
- Se un download si interrompe, rilancia lo stesso comando: i file già completati vengono saltati
- Errori 403 frequenti → aspetta qualche minuto e riprova
- Su server senza terminale interattivo il tasto Q non è disponibile — usa `kill` o `Ctrl+C`

---

## ❓ Risoluzione problemi

| Problema | Soluzione |
|---|---|
| Nessun episodio trovato | Controlla che l'URL sia corretto |
| m3u8 non trovato | L'episodio potrebbe essere stato rimosso dal sito |
| Errore 403 | Riduci i worker o aspetta prima di riprovare |
| Audio in inglese | Il sito non ha il doppiaggio italiano per quella serie |
| Dipendenze mancanti | `pip install -r requirements.txt` |
| `externally-managed-environment` su Linux | Usa un virtualenv |

---

## 👤 Autore

Creato da **msandy-13** 🇮🇹 — l'ho creato per divertimento, spero possa esservi utile.

---

## 📄 Licenza

**MIT** — libero uso, modifica e distribuzione.
