#!/usr/bin/env python3
"""
Downloader per guarda-serie.click
Catena: guarda-serie.click (data-link) → supervideo.cc/e/{ID} → master.m3u8 → yt-dlp
"""

from __future__ import annotations


import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import re

import typer
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table
import cloudscraper
from bs4 import BeautifulSoup
import yt_dlp

app = typer.Typer(pretty_exceptions_show_locals=False)
console = Console()

TASK_COLOR = "cyan"
stop_event = threading.Event()

# ── Key listener cross-platform (Windows + Linux) ────────────────────────────

def key_listener():
    """Ascolta Q o Ctrl+C in background — funziona su Windows e Linux."""
    try:
        if os.name == "nt":
            import msvcrt
            while not stop_event.is_set():
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ('\x03', 'q', 'Q'):
                        stop_event.set()
                        os._exit(0)
        else:
            import termios, tty, select
            if not sys.stdin.isatty():
                return
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while not stop_event.is_set():
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key in ('\x03', 'q', 'Q'):
                            stop_event.set()
                            os._exit(0)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except Exception:
        pass  # Terminale non interattivo o non supportato — ignora

# ── Scraper ───────────────────────────────────────────────────────────────────

def make_scraper() -> cloudscraper.CloudScraper:
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

HEADERS_GUARDA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://guarda-serie.click/",
}

HEADERS_SUPERVIDEO = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) "
                  "Gecko/20100101 Firefox/148.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": "https://supervideo.cc/",
}

# ── Deobfuscator ──────────────────────────────────────────────────────────────

def deobfuscate_pack(p: str, a: int, c: int, k: list[str]) -> str:
    def base_n(num: int, base: int) -> str:
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return "0"
        result = ""
        while num > 0:
            result = chars[num % base] + result
            num //= base
        return result
    for i in range(c - 1, -1, -1):
        if k[i]:
            p = re.sub(r"\b" + re.escape(base_n(i, a)) + r"\b", k[i], p)
    return p


def extract_m3u8_from_html(html: str) -> str | None:
    m = re.search(
        r"eval\(function\(p,a,c,k,e,d\)\{[^}]+\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)\)\)",
        html, re.DOTALL
    )
    if not m:
        return None
    decoded = deobfuscate_pack(
        m.group(1), int(m.group(2)), int(m.group(3)), m.group(4).split("|")
    )
    hit = re.search(r"(https://[^\s\"'\\]+master\.m3u8[^\s\"'\\]*)", decoded)
    if hit:
        return hit.group(1).replace("\\/", "/")
    hit2 = re.search(r"(https://[^\s\"'\\]+\.m3u8\?t=[^\s\"'\\]+)", decoded)
    if hit2:
        return hit2.group(1).replace("\\/", "/")
    return None

# ── Scraping ──────────────────────────────────────────────────────────────────

def extract_episodes(page_url: str, scraper: cloudscraper.CloudScraper) -> tuple[str, list[dict]]:
    resp = scraper.get(page_url, headers=HEADERS_GUARDA, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("h1") or soup.find("title")
    serie_title = title_tag.get_text(strip=True) if title_tag else "Serie"
    serie_title = re.sub(r"\s*[-–|].*streaming.*", "", serie_title, flags=re.IGNORECASE).strip()

    episodes = []
    for a in soup.find_all("a", id=re.compile(r"^serie-\d+_\d+$")):
        data_num   = a.get("data-num", "")
        data_title = a.get("data-title", "")
        if not data_num:
            continue

        # Raccogli tutti i player dal div.mirrors
        players = []
        li = a.parent
        mirrors = li.find("div", class_="mirrors") if li else None
        if mirrors:
            for m in mirrors.find_all("a", class_="mr"):
                link = m.get("data-link", "")
                if link and link != "#":
                    players.append(link)
        # Fallback: usa data-link del tag principale
        if not players:
            main_link = a.get("data-link", "")
            if main_link and main_link != "#":
                players.append(main_link)

        if not players:
            continue

        # Normalizza data_num in formato SxEE con zero padding (es. 1x5 → 1x05)
        if data_num and "x" in data_num:
            s, e = data_num.split("x", 1)
            data_num_fmt = f"{s}x{e.zfill(2)}"
        else:
            data_num_fmt = data_num

        if data_title:
            short = data_title.split(":")[0].strip()
            title = f"{data_num_fmt} - {short}" if data_num_fmt else short
        else:
            title = data_num_fmt or "Episodio"

        episodes.append({"num": data_num, "title": title, "players": players})

    # Deduplicazione per num mantenendo ordine
    seen: dict[str, dict] = {}
    for ep in episodes:
        seen[ep["num"]] = ep
    return serie_title, list(seen.values())


def fetch_m3u8(player_url: str, scraper: cloudscraper.CloudScraper) -> str | None:
    """Funziona con qualsiasi player che usa eval() offuscato (supervideo, dr0pstream, ecc.)"""
    resp = scraper.get(player_url, headers=HEADERS_SUPERVIDEO, timeout=20)
    resp.raise_for_status()
    return extract_m3u8_from_html(resp.text)

# ── Utility ───────────────────────────────────────────────────────────────────

def clean_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    return re.sub(r"\s+", " ", name).strip() or "Episodio"


def parse_stagioni(stagioni_str: str) -> list[dict]:
    """
    Parsa la stringa --stagioni "2 1 10/4 3 15"
    Ritorna lista di {'st': int, 'ep': int, 'stop': int}
    Formato blocco: "ST EP STOP" separati da spazio, blocchi separati da /
    EP e STOP sono opzionali (default: 1 e 0=fino alla fine)
    """
    result = []
    for blocco in stagioni_str.split("/"):
        parts = blocco.strip().split()
        if not parts:
            continue
        try:
            st   = int(parts[0])
            ep   = int(parts[1]) if len(parts) > 1 else 1
            stop = int(parts[2]) if len(parts) > 2 else 0
            result.append({"st": st, "ep": ep, "stop": stop})
        except ValueError:
            continue
    return result

# ── Progress UI ───────────────────────────────────────────────────────────────

def create_progress_bar() -> Progress:
    return Progress(
        "{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        "•",
        TimeRemainingColumn(),
    )


def create_progress_table(title: str, job_progress: Progress) -> Table:
    progress_table = Table.grid()
    progress_table.add_row(
        Panel.fit(
            job_progress,
            title=f"[b]{title}",
            border_style="red",
            padding=(1, 1),
        )
    )
    return progress_table

# ── Download singolo episodio ─────────────────────────────────────────────────

def download_episode(
    ep: dict,
    output: Path,
    format_str: str,
    job_progress: Progress,
    task_id,
    overall_task_id,
) -> bool:
    if stop_event.is_set():
        job_progress.advance(overall_task_id)
        return False

    def progress_hook(d: dict) -> None:
        if d["status"] == "downloading":
            pct_str = d.get("_percent_str", "0%").strip().replace("%", "").replace("~", "")
            try:
                job_progress.update(task_id, completed=float(pct_str))
            except ValueError:
                pass
        elif d["status"] == "finished":
            job_progress.update(task_id, completed=100, visible=False)
            job_progress.advance(overall_task_id)

    # Scegli referer in base al player usato
    m3u8 = ep["m3u8"]
    if "dropcdn.io" in m3u8 or "dropload" in m3u8:
        referer = "https://dr0pstream.com/"
        origin  = "https://dr0pstream.com"
    else:
        referer = "https://supervideo.cc/"
        origin  = "https://supervideo.cc"

    ydl_opts = {
        "outtmpl":          str(output / f"{clean_filename(ep['title'])}.%(ext)s"),
        "format":           format_str,
        "quiet":            True,
        "no_warnings":      True,
        "noprogress":       True,
        "continuedl":       True,
        "retries":          20,
        "fragment_retries": 20,
        "socket_timeout":   5,
        "http_chunk_size":  512 * 1024,
        "http_headers": {
            "Referer":    referer,
            "Origin":     origin,
            "User-Agent": HEADERS_SUPERVIDEO["User-Agent"],
        },
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
    }

    try:
        job_progress.update(task_id, visible=True)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ep["m3u8"]])
        return True
    except Exception:
        job_progress.update(task_id, visible=False)
        job_progress.advance(overall_task_id)
        return False

# ── CLI ───────────────────────────────────────────────────────────────────────

@app.command()
def download(
    url:          str  = typer.Argument(...,                help="URL della pagina serie"),
    output:       Path = typer.Option(Path("./downloads"), "--output",   "-o"),
    quality:      str  = typer.Option("best",              "--quality",  "-q", help="best / 1080 / 720 / worst"),
    dry_run:      bool = typer.Option(False,               "--dry-run",        help="Solo lista link"),
    st:           int  = typer.Option(0,    "--st",   help="Stagione singola (0 = tutte)"),
    ep:           int  = typer.Option(1,    "--ep",   help="Episodio di inizio (con --st)"),
    stop:         int  = typer.Option(0,    "--stop", help="Episodio di fine (con --st, 0 = fine)"),
    stagioni:     str  = typer.Option("",  "--stagioni", help='Più stagioni: "2 1 10/4 3 15" = st2 ep1-10, st4 ep3-15'),
    workers:      int  = typer.Option(2,                   "--workers",  "-w", help="Download paralleli"),
):
    scraper = make_scraper()

    # Avvia key listener in background (solo durante il download)
    listener = threading.Thread(target=key_listener, daemon=True)

    with console.status("[cyan]Cerco episodi..."):
        serie_title, episodes = extract_episodes(url, scraper)

    if not episodes:
        console.print("[red]❌ Nessun episodio trovato.[/]")
        raise typer.Exit(1)

    # Estrai numero episodio dalla stringa "SxEE"
    def ep_num(e: dict) -> int:
        try:
            return int(e["num"].split("x")[1])
        except (IndexError, ValueError):
            return 0

    def ep_st(e: dict) -> int:
        try:
            return int(e["num"].split("x")[0])
        except (IndexError, ValueError):
            return 0

    if stagioni:
        # Modalità multi-stagione: "2 1 10/4 3 15"
        blocchi = parse_stagioni(stagioni)
        filtered = []
        for b in blocchi:
            for e in episodes:
                if ep_st(e) != b["st"]:
                    continue
                n = ep_num(e)
                if n < b["ep"]:
                    continue
                if b["stop"] and n > b["stop"]:
                    continue
                filtered.append(e)
        episodes = filtered
    elif st:
        # Modalità singola stagione
        episodes = [e for e in episodes if e["num"].startswith(f"{st}x")]
        if ep > 1:
            episodes = [e for e in episodes if ep_num(e) >= ep]
        if stop:
            episodes = [e for e in episodes if ep_num(e) <= stop]

    # Costruisci cartella: downloads/NomeSerie/Stagione X  (o downloads/NomeSerie se no --st)
    serie_folder = clean_filename(serie_title)
    # final_output base — la cartella stagione viene gestita per episodio
    base_output = output / serie_folder
    base_output.mkdir(parents=True, exist_ok=True)

    def get_episode_output(e: dict) -> Path:
        """Restituisce la cartella corretta per l'episodio in base alla stagione."""
        s = ep_st(e)
        if s:
            folder = base_output / f"Stagione {s}"
            folder.mkdir(parents=True, exist_ok=True)
            return folder
        return base_output

    final_output = base_output  # usato solo per il messaggio finale

    resolved: list[dict] = []
    with console.status("[cyan]Risolvo stream...") as status:
        for i, ep in enumerate(episodes, 1):
            status.update(f"[cyan]Risolvo [{i}/{len(episodes)}] {ep['title'][:40]}...")
            m3u8_url = None
            used_player = None
            for j, player_url in enumerate(ep["players"], 1):
                try:
                    m3u8_url = fetch_m3u8(player_url, scraper)
                    if m3u8_url:
                        used_player = j
                        break
                except Exception:
                    continue
            if not m3u8_url:
                console.print(f"  [red]✗[/] {ep['title']} → nessun player funzionante")
                continue
            resolved.append({**ep, "m3u8": m3u8_url})

        # Skip episodi già scaricati
        skipped = 0
        to_download = []
        for e in resolved:
            ep_folder = get_episode_output(e)
            expected = ep_folder / f"{clean_filename(e['title'])}.mp4"
            if expected.exists():
                skipped += 1
            else:
                to_download.append(e)
        if skipped:
            console.print(f"[dim]⏭ {skipped} episodi già scaricati, skip[/]")
        resolved = to_download

    if not resolved:
        console.print("[red]❌ Nessun stream risolvibile.[/]")
        raise typer.Exit(1)

    if dry_run:
        for i, ep in enumerate(resolved, 1):
            console.print(f"[dim]{i:>3}.[/] [bold]{ep['title']}[/]\n     [blue dim]{ep['m3u8']}[/]")
        return

    if quality == "best":
        format_str = "bestvideo+bestaudio/best"
    elif quality == "worst":
        format_str = "worstvideo+worstaudio/worst"
    elif quality.isdigit():
        format_str = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
    else:
        format_str = "bestvideo+bestaudio/best"

    job_progress = create_progress_bar()
    progress_table = create_progress_table(serie_title, job_progress)
    n = len(resolved)
    overall_task = job_progress.add_task(f"[{TASK_COLOR}]Progress", total=n, visible=True)
    ep_tasks = []
    for i, ep in enumerate(resolved):
        short = ep["title"][:35] + "…" if len(ep["title"]) > 35 else ep["title"]
        t = job_progress.add_task(
            f"[{TASK_COLOR}]Episode {i+1}/{n}  {short}",
            total=100,
            visible=False,
        )
        ep_tasks.append(t)

    ok = fail = 0

    # Clear terminale prima del download
    os.system("cls" if os.name == "nt" else "clear")

    # Avvia listener tasti solo durante il download
    listener.start()
    console.print("[dim]Premi Q per interrompere[/]")

    with Live(progress_table, console=console, refresh_per_second=10):
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    download_episode,
                    ep, get_episode_output(ep), format_str, job_progress, ep_tasks[i], overall_task
                ): i
                for i, ep in enumerate(resolved)
            }
            for future in as_completed(futures):
                if stop_event.is_set():
                    break
                if future.result():
                    ok += 1
                else:
                    fail += 1

    console.print(f"\n[bold green]✅ Completato:[/] {ok} OK, {fail} falliti → [white]{final_output}[/]")


if __name__ == "__main__":
    app()
