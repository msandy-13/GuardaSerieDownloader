# 🎬 GuardaSerie Downloader

<p align="center">
  <img src="https://via.placeholder.com/900x300?text=GuardaSerie+Downloader" alt="preview">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg">
  <img src="https://github.com/msandy-13/GuardaSerieDownloader.svg?style=social">
</p>

**Downloader CLI potente per guarda-serie.click**
Scarica intere serie in **MP4** direttamente dagli stream HLS *(supervideo.cc + fallback dr0pstream)* usando **yt-dlp**.

---

## ⚠️ Disclaimer importante

Questo tool è stato creato **solo per scopi educativi e personali**.
L’autore non è responsabile per alcun uso improprio del software.

* Scaricare contenuti protetti da copyright senza autorizzazione può violare le leggi del tuo Paese
* Usa questo script **solo su contenuti di cui possiedi i diritti**
* L’autore **non incoraggia né supporta la pirateria**
* **Usa a tuo rischio e pericolo**

---

## ✨ Features principali

* 🎯 Estrazione automatica di tutti gli episodi dalla pagina della serie
* 🔍 Risoluzione intelligente dei player offuscati con fallback automatico
* ⚡ Download parallelo *(3-4 worker consigliati)*
* 📁 Organizzazione automatica: `Serie / Stagione X / Episodio.mp4`
* ♻️ Skip file già scaricati + resume download interrotti
* 🎛️ Supporto per range episodi, multi-stagioni e qualità personalizzata
* 📊 Progress bar in tempo reale *(Rich)*
* ⏹️ Premi **Q** per interrompere tutto

---

## 🔧 Come funziona

1. Analizza la pagina della serie su **guarda-serie.click**
2. Estrae i player (supervideo, fallback)
3. Deoffusca il codice per ottenere il link **.m3u8**
4. Usa **yt-dlp** per scaricare e convertire in MP4
5. Organizza automaticamente i file

Tutto avviene **in locale sul tuo PC**.

---

## ⚙️ Requisiti

* Python **3.9+**
* Connessione stabile

---

## 🚀 Installazione

```bash
git clone https://github.com/msandy-13/guarda-serie-downloader.git
cd guarda-serie-downloader

pip install -r requirements.txt
```

### Opzione comando globale

```bash
pip install -e .
```

Poi puoi usare:

```bash
guarda-serie "URL_DELLA_SERIE"
```

---

## 📖 Utilizzo base

```bash
python downloader.py "https://guarda-serie.click/serietv/3176-adventure-time-streaming-ita.html"
```

---

## 🎛️ Opzioni principali

| Opzione         | Default       | Descrizione                        |
| --------------- | ------------- | ---------------------------------- |
| `--output, -o`  | `./downloads` | Cartella di destinazione           |
| `--quality, -q` | `best`        | Qualità: best, 1080, 720, worst    |
| `--st`          | `0`           | Stagione singola (0 = tutte)       |
| `--ep`          | `1`           | Episodio iniziale                  |
| `--stop`        | `0`           | Episodio finale                    |
| `--stagioni`    | —             | Multi-stagioni (`"2 1 10/4 3 15"`) |
| `--workers, -w` | `2`           | Download paralleli                 |
| `--dry-run`     | `False`       | Solo preview link                  |

---

## ⚡ Esempi veloci

```bash
# Stagione completa
python downloader.py <URL> --st 3

# Episodi specifici
python downloader.py <URL> --st 2 --ep 5 --stop 10

# Multi-stagioni
python downloader.py <URL> --stagioni "2 1 10/4 3 15"

# 720p con 3 download
python downloader.py <URL> --quality 720 --workers 3
```

---

## 📁 Struttura cartelle

```bash
downloads/
└── Nome Serie/
    ├── Stagione 1/
    ├── Stagione 2/
    └── ...
```

---

## 💡 Consigli d’uso

* Usa `--workers 2` se è la prima volta
* Non superare **3-4 worker**
* Se vedi errori 403 → aspetta e riprova
* Usa `--dry-run` per testare prima
* Puoi rilanciare il comando: i file già scaricati vengono saltati

---

## ⏸️ Durante il download

* Premi **Q** per fermare tutto
* Resume automatico dei download
* Skip automatico dei file già presenti

---

## ❓ Risoluzione problemi

| Problema                | Soluzione                         |
| ----------------------- | --------------------------------- |
| Nessun episodio trovato | Controlla URL                     |
| m3u8 non trovato        | Episodio rimosso                  |
| Errore 403              | Riduci workers                    |
| Dipendenze mancanti     | `pip install -r requirements.txt` |

---

## 👤 Autore

Creato da **msandy-13** 🇮🇹

---

## ❤️ Nota

Progetto semplice, senza complicazioni.
L’ho fatto perché mi serviva — magari serve anche a qualcun altro.

---

## 📄 License

Licenza **MIT** — libero uso, modifica e distribuzione.

---

> Made with ❤️ per chi vuole guardare le serie senza pubblicità e senza stress
