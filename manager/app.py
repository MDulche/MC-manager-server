from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
import asyncio
import threading
import time
import subprocess
import requests as http_req
from core.process_manager import (
    start_server, stop_server, stop_server_graceful, backup_world,
    send_command, is_running, get_logs, _log_buffer,
    list_worlds, get_current_world, switch_world, create_new_world,
    delete_world, list_world_backups, restore_backup,
    get_server_properties, update_server_properties, get_whitelist,
    add_to_whitelist, remove_from_whitelist, kick_player, ban_player,
    apply_gamerule, restart_server,
    check_for_whitelist_requests, approve_whitelist_request, reject_whitelist_request,
    get_world_config, save_world_config, apply_world_config, check_server_installed,
    get_current_server_version, get_latest_minecraft_version,
    install_minecraft_server, update_minecraft_server
)

# ── App ────────────────────────────────────────────────────────
app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# ── Manager auto-update ────────────────────────────────────────
_update_cache = {"status": "checking"}

def _fetch_update_info():
    global _update_cache
    try:
        res = http_req.get(
            "https://api.github.com/repos/MDulche/MC-manager-server/releases/latest",
            headers={"Accept": "application/vnd.github+json"},
            timeout=5
        )
        if res.status_code != 200:
            _update_cache = {"status": "error", "message": f"GitHub {res.status_code}"}
            return
        latest     = res.json()
        latest_tag = latest["tag_name"]
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True,
            cwd=Path.home() / "minecraft-manager"
        )
        local_tag = result.stdout.strip() if result.returncode == 0 else "inconnue"
        if latest_tag != local_tag:
            _update_cache = {
                "status":  "update_available",
                "current": local_tag,
                "latest":  latest_tag,
                "url":     latest["html_url"]
            }
        else:
            _update_cache = {"status": "up_to_date", "version": local_tag}
    except Exception as e:
        _update_cache = {"status": "error", "message": str(e)}

# ── Auto-restart ───────────────────────────────────────────────
def auto_restart():
    if is_running():
        send_command("say §c[AUTO-RESTART] Redémarrage dans 1 minute!")
        time.sleep(30)
        send_command("say §c[AUTO-RESTART] Redémarrage dans 30 secondes!")
        time.sleep(20)
        send_command("say §c[AUTO-RESTART] Redémarrage dans 10 secondes!")
        time.sleep(10)
        stop_server()
        time.sleep(5)
        start_server()

# ── Scheduler ──────────────────────────────────────────────────
scheduler = BackgroundScheduler()
scheduler.add_job(backup_world,       "interval", minutes=30, id="auto_backup")
scheduler.add_job(auto_restart,       "interval", hours=2.5,  id="auto_restart")
scheduler.add_job(_fetch_update_info, "interval", hours=6,    id="check_manager_update")
scheduler.start()

# ============================================================
# ROUTES
# ============================================================

@app.on_event("startup")
async def on_startup():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _fetch_update_info)

@app.get("/")
async def index(request: Request):
    server_installed = check_server_installed()
    current_version = get_current_server_version() if server_installed else None
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "server_installed": server_installed,
        "server_version": current_version,
        "running": is_running(),
        "logs": get_logs()
    })

@app.get("/logs")
async def get_logs_endpoint():
    return get_logs()

@app.get("/status")
async def get_status():
    return {"running": is_running()}

@app.get("/backups")
async def list_backups():
    backup_dir = Path.home() / "minecraft-manager" / "backups" / "worlds"
    if not backup_dir.exists():
        return []
    backups = sorted(backup_dir.glob("*.zip"), reverse=True)
    return [{"name": b.name, "size": b.stat().st_size, "date": b.stat().st_mtime} for b in backups]

@app.get("/worlds")
async def get_worlds():
    return {"worlds": list_worlds(), "current": get_current_world()}

@app.get("/server-config")
async def get_config():
    current_world_name = get_current_world()
    world_config = get_world_config(current_world_name)
    return {
        "max_players": str(world_config["max_players"]),
        "whitelist_enabled": "true" if world_config["whitelist_enabled"] else "false"
    }

@app.post("/update-config")
async def update_config(max_players: str = Form(...), enable_whitelist: str = Form(...)):
    def update_and_restart():
        current_world_name = get_current_world()
        world_config = get_world_config(current_world_name)
        world_config["max_players"] = int(max_players)
        world_config["whitelist_enabled"] = (enable_whitelist == "true")
        world_config["whitelist_players"] = get_whitelist()
        save_world_config(current_world_name, world_config)
        if is_running():
            stop_server()
            time.sleep(3)
        apply_world_config(current_world_name)
        time.sleep(2)
        start_server()
    threading.Thread(target=update_and_restart, daemon=True).start()
    return RedirectResponse(url="/", status_code=303)

@app.get("/whitelist")
async def get_whitelist_route():
    return get_whitelist()

@app.post("/whitelist-add")
async def whitelist_add(username: str = Form(...)):
    add_to_whitelist(username)
    return RedirectResponse(url="/", status_code=303)

@app.post("/whitelist-remove")
async def whitelist_remove(username: str = Form(...)):
    remove_from_whitelist(username)
    return RedirectResponse(url="/", status_code=303)

@app.post("/kick")
async def kick(username: str = Form(...)):
    kick_player(username)
    return RedirectResponse(url="/", status_code=303)

@app.post("/ban")
async def ban(username: str = Form(...)):
    ban_player(username)
    return RedirectResponse(url="/", status_code=303)

@app.post("/gamerule")
async def gamerule(rule: str = Form(...), value: str = Form(...)):
    apply_gamerule(rule, value)
    return RedirectResponse(url="/", status_code=303)

@app.post("/switch-world")
async def switch_world_route(world: str = Form(...)):
    switch_world(world)
    return RedirectResponse(url="/", status_code=303)

@app.post("/create-world")
async def create_world_route(world_name: str = Form(...)):
    create_new_world(world_name)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-world")
async def delete_world_route(world_name: str = Form(...)):
    delete_world(world_name)
    return RedirectResponse(url="/", status_code=303)

@app.get("/world-backups/{world_name}")
async def get_world_backups(world_name: str):
    return list_world_backups(world_name)

@app.post("/restore-backup")
async def restore_backup_route(world_name: str = Form(...), backup_file: str = Form(...)):
    restore_backup(world_name, backup_file)
    return RedirectResponse(url="/", status_code=303)

@app.post("/backup")
async def backup():
    backup_world()
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop-graceful")
async def stop_graceful():
    threading.Thread(target=stop_server_graceful, daemon=True).start()
    return RedirectResponse(url="/", status_code=303)

@app.post("/restart")
async def restart():
    threading.Thread(target=restart_server, daemon=True).start()
    return RedirectResponse(url="/", status_code=303)

@app.post("/start")
async def start():
    start_server()
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop")
async def stop():
    stop_server()
    return RedirectResponse(url="/", status_code=303)

@app.post("/command")
async def command(cmd: str = Form(...)):
    if cmd.strip():
        send_command(cmd)
    return RedirectResponse(url="/", status_code=303)

@app.get("/logs/stream")
async def log_stream():
    async def event_generator():
        last_len = len(_log_buffer)
        yield "data: [CONNECTED]\n\n"
        while True:
            await asyncio.sleep(0.5)
            current_len = len(_log_buffer)
            if current_len > last_len:
                new_logs = list(_log_buffer)[-15:]
                yield f"data: {chr(10).join(new_logs)}\n\n"
                last_len = current_len
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# ============================================================
# ROUTES INSTALLATION / MISE À JOUR SERVEUR MINECRAFT
# ============================================================

@app.get("/server-status")
async def server_status():
    installed = check_server_installed()
    current_version = get_current_server_version() if installed else None
    latest = get_latest_minecraft_version()
    return {
        "installed": installed,
        "current_version": current_version,
        "latest_version": latest["version"] if latest else None,
        "update_available": (current_version != latest["version"]) if current_version and latest else False
    }

@app.get("/install-server-form")
async def install_server_form(request: Request):
    latest = get_latest_minecraft_version()
    return templates.TemplateResponse("install_server.html", {
        "request": request,
        "latest_version": latest["version"] if latest else "Erreur API",
        "download_url": latest["url"] if latest else "",
        "size_mb": latest["size_mb"] if latest else 0
    })

@app.post("/install-server")
async def install_server_action(download_url: str = Form(...)):
    def install_thread():
        result = install_minecraft_server(download_url)
        print("[INSTALL] ✓" if result["success"] else f"[INSTALL] ✗ {result.get('error')}")
    threading.Thread(target=install_thread, daemon=True).start()
    return RedirectResponse(url="/?install_started=true", status_code=303)

@app.get("/update-server-form")
async def update_server_form(request: Request):
    current_version = get_current_server_version()
    latest = get_latest_minecraft_version()
    return templates.TemplateResponse("update_server.html", {
        "request": request,
        "current_version": current_version or "Inconnue",
        "latest_version": latest["version"] if latest else "Erreur API",
        "download_url": latest["url"] if latest else "",
        "size_mb": latest["size_mb"] if latest else 0
    })

@app.post("/update-server")
async def update_server_action(download_url: str = Form(...)):
    def update_thread():
        result = update_minecraft_server(download_url)
        print("[UPDATE] ✓" if result["success"] else f"[UPDATE] ✗ {result.get('error')}")
    threading.Thread(target=update_thread, daemon=True).start()
    return RedirectResponse(url="/?update_started=true", status_code=303)

# ============================================================
# ROUTES MANAGER AUTO-UPDATE
# ============================================================

@app.get("/api/updates")
async def get_updates():
    return _update_cache

@app.post("/api/do-update")
async def do_update():
    def _update():
        try:
            repo_dir = Path.home() / "minecraft-manager"
            subprocess.run(["git", "pull"], cwd=repo_dir, check=True)
            subprocess.run(["pip", "install", "-r", "manager/requirements.txt", "-q"],
                           cwd=repo_dir, check=True)
            print("[MANAGER-UPDATE] ✓ Mise à jour appliquée")
            _fetch_update_info()
        except Exception as e:
            print(f"[MANAGER-UPDATE] ✗ Erreur : {e}")
    threading.Thread(target=_update, daemon=True).start()
    return {"status": "updating"}