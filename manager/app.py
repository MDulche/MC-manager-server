from fastapi import FastAPI, Request, Form
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import threading
import time
from core.process_manager import (
    start_server, stop_server, stop_server_graceful, backup_world,
    send_command, is_running, get_logs, _log_buffer,
    list_worlds, get_current_world, switch_world, create_new_world,
    delete_world, list_world_backups, restore_backup,
    get_server_properties, update_server_properties, get_whitelist,
    add_to_whitelist, remove_from_whitelist, kick_player, ban_player,
    apply_gamerule, restart_server,
    check_for_whitelist_requests, approve_whitelist_request, reject_whitelist_request,
    get_world_config, save_world_config, apply_world_config, check_server_installed, get_current_server_version, get_latest_minecraft_version,
    install_minecraft_server, update_minecraft_server
)



app = FastAPI()
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# ============================================================
# SCHEDULER AUTOMATIQUE
# ============================================================

def auto_restart():
    """Restart serveur proprement"""
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

# Initialiser scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(backup_world, 'interval', minutes=30, id='auto_backup')
scheduler.add_job(auto_restart, 'interval', hours=2.5, id='auto_restart')
scheduler.start()

# ============================================================
# ROUTES
# ============================================================



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
    return {
        "worlds": list_worlds(),
        "current": get_current_world()
    }

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
    import threading
    
    def update_and_restart():
        current_world_name = get_current_world()
        print(f"[DEBUG] Monde actuel: {current_world_name}")
        
        # Sauvegarder config monde AVANT arrêt
        world_config = get_world_config(current_world_name)
        print(f"[DEBUG] Config avant: {world_config}")
        
        world_config["max_players"] = int(max_players)
        world_config["whitelist_enabled"] = (enable_whitelist == "true")
        world_config["whitelist_players"] = get_whitelist()  # Capturer whitelist actuelle
        
        save_world_config(current_world_name, world_config)
        print(f"[DEBUG] Config sauvegardée: {world_config}")
        
        # Vérifier fichier créé
        import json
        config_file = Path.home() / "minecraft-manager" / "worlds" / current_world_name / "config.json"
        print(f"[DEBUG] Fichier existe: {config_file.exists()}")
        if config_file.exists():
            print(f"[DEBUG] Contenu fichier: {config_file.read_text()}")
        
        # Arrêter serveur
        if is_running():
            stop_server()
            time.sleep(3)
        
        # Appliquer config
        apply_world_config(current_world_name)
        print(f"[DEBUG] Config appliquée")
        
        # Redémarrer
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
    result = switch_world(world)
    return RedirectResponse(url="/", status_code=303)

@app.post("/create-world")
async def create_world_route(world_name: str = Form(...)):
    result = create_new_world(world_name)
    return RedirectResponse(url="/", status_code=303)

@app.post("/delete-world")
async def delete_world_route(world_name: str = Form(...)):
    result = delete_world(world_name)
    return RedirectResponse(url="/", status_code=303)

@app.get("/world-backups/{world_name}")
async def get_world_backups(world_name: str):
    return list_world_backups(world_name)

@app.post("/restore-backup")
async def restore_backup_route(world_name: str = Form(...), backup_file: str = Form(...)):
    result = restore_backup(world_name, backup_file)
    return RedirectResponse(url="/", status_code=303)

@app.post("/backup")
async def backup():
    result = backup_world()
    return RedirectResponse(url="/", status_code=303)

@app.post("/stop-graceful")
async def stop_graceful():
    threading.Thread(target=stop_server_graceful, daemon=True).start()
    return RedirectResponse(url="/", status_code=303)

@app.post("/restart")
async def restart():
    import threading
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
                data_lines = '\n'.join(new_logs)
                yield f"data: {data_lines}\n\n"
                last_len = current_len

    return StreamingResponse(event_generator(), media_type="text/event-stream")
# ============================================================
# ROUTES INSTALLATION / MISE À JOUR SERVEUR
# ============================================================

@app.get("/server-status")
async def server_status():
    """Statut installation serveur"""
    installed = check_server_installed()
    current_version = get_current_server_version() if installed else None
    latest = get_latest_minecraft_version()
    
    return {
        "installed": installed,
        "current_version": current_version,
        "latest_version": latest["version"] if latest else None,
        "latest_url": latest["url"] if latest else None,
        "latest_size_mb": latest["size_mb"] if latest else None,
        "update_available": (current_version and latest and current_version != latest["version"]) if current_version and latest else False
    }


@app.get("/install-server-form")
async def install_server_form(request: Request):
    """Formulaire installation serveur"""
    latest = get_latest_minecraft_version()
    
    return templates.TemplateResponse("install_server.html", {
        "request": request,
        "latest_version": latest["version"] if latest else "Erreur API",
        "download_url": latest["url"] if latest else "",
        "size_mb": latest["size_mb"] if latest else 0
    })


@app.post("/install-server")
async def install_server_action(download_url: str = Form(...)):
    """Action installation serveur"""
    import threading
    
    def install_thread():
        result = install_minecraft_server(download_url)
        if result["success"]:
            print("[INSTALL] ✓ Installation terminée")
        else:
            print(f"[INSTALL] ✗ Erreur: {result.get('error', 'Erreur inconnue')}")
    
    threading.Thread(target=install_thread, daemon=True).start()
    
    return RedirectResponse(url="/?install_started=true", status_code=303)


@app.get("/update-server-form")
async def update_server_form(request: Request):
    """Formulaire mise à jour serveur"""
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
    """Action mise à jour serveur"""
    import threading
    
    def update_thread():
        result = update_minecraft_server(download_url)
        if result["success"]:
            print("[UPDATE] ✓ Mise à jour terminée")
        else:
            print(f"[UPDATE] ✗ Erreur: {result.get('error', 'Erreur inconnue')}")
    
    threading.Thread(target=update_thread, daemon=True).start()
    
    return RedirectResponse(url="/?update_started=true", status_code=303)
