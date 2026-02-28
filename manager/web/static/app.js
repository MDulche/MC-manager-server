/* =============================================================================
   Minecraft Manager — app.js
   À placer dans web/static/app.js
   ============================================================================= */

/* ── Utilitaire : soumettre un POST sans formulaire visible ──────────────── */
function postAction(url, params) {
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    Object.entries(params).forEach(([n, v]) => {
        const i = document.createElement('input');
        i.type = 'hidden'; i.name = n; i.value = v;
        form.appendChild(i);
    });
    document.body.appendChild(form);
    form.submit();
}

/* ══════════════════════════════════════════════════════════════════════════
   DASHBOARD
   ══════════════════════════════════════════════════════════════════════════ */

/* ── Config serveur ─────────────────────────────────────────────────────── */
async function loadConfig() {
    try {
        const res = await fetch('/server-config');
        const config = await res.json();
        document.getElementById('max-players').value = config.max_players;
        document.getElementById('enable-whitelist').checked = config.whitelist_enabled === 'true';
    } catch(e) {}
}

function saveConfig() {
    if (!confirm('Le serveur va redémarrer automatiquement pour appliquer. Continuer?')) return;
    postAction('/update-config', {
        max_players:      document.getElementById('max-players').value,
        enable_whitelist: document.getElementById('enable-whitelist').checked ? 'true' : 'false'
    });
}

/* ── Whitelist ───────────────────────────────────────────────────────────── */
async function loadWhitelist() {
    try {
        const players = await (await fetch('/whitelist')).json();
        const div = document.getElementById('whitelist-players');
        if (!div) return;
        if (players.length === 0) {
            div.innerHTML = '<p class="text-muted">Aucun joueur</p>';
        } else {
            div.innerHTML = players.map(p => `
                <div class="player-item">
                    <strong>${p.name}</strong>
                    <div class="btn-row" style="margin:0; gap:4px;">
                        <button class="btn btn-orange btn-sm" onclick="kickPlayer('${p.name}')">👢 Kick</button>
                        <button class="btn btn-red btn-sm"    onclick="banPlayer('${p.name}')">🚫 Ban</button>
                        <button class="btn btn-grey btn-sm"   onclick="removeWhitelist('${p.name}')">❌ Retirer</button>
                    </div>
                </div>`).join('');
        }
    } catch(e) {}
}

function addWhitelist() {
    const u = document.getElementById('whitelist-username').value.trim();
    if (!u) return;
    postAction('/whitelist-add', { username: u });
}
function removeWhitelist(u) { if (confirm(`Retirer ${u} de la whitelist?`)) postAction('/whitelist-remove', { username: u }); }
function kickPlayer(u)       { if (confirm(`Kick ${u}?`))                   postAction('/kick',             { username: u }); }
function banPlayer(u)        { if (confirm(`BAN ${u}?`))                    postAction('/ban',              { username: u }); }

/* ── Gamerules ───────────────────────────────────────────────────────────── */
function applyGamerule(rule, value) { postAction('/gamerule', { rule, value }); }

/* ── Mondes ─────────────────────────────────────────────────────────────── */
function switchWorld() {
    const s = document.getElementById('world-select');
    if (!s || !s.value) return alert('Sélectionnez un monde');
    if (!confirm('Serveur doit être arrêté. Continuer?')) return;
    postAction('/switch-world', { world: s.value });
}

function deleteWorld() {
    const s = document.getElementById('world-select');
    if (!s || !s.value) return alert('Sélectionnez un monde');
    if (!confirm(`Supprimer '${s.value}' et TOUS ses backups ?`)) return;
    postAction('/delete-world', { world_name: s.value });
}

async function showBackups() {
    const s = document.getElementById('world-select');
    if (!s || !s.value) return alert('Sélectionnez un monde');
    const worldName = s.value;
    document.getElementById('backup-world-name').textContent = worldName;
    const panel = document.getElementById('backups-panel');
    if (panel) panel.style.display = 'block';
    try {
        const backups = await (await fetch(`/world-backups/${worldName}`)).json();
        const list = document.getElementById('backups-list');
        if (backups.length === 0) {
            list.innerHTML = '<p class="text-muted">Aucun backup</p>';
        } else {
            list.innerHTML = backups.map(b => {
                const date   = new Date(b.date * 1000).toLocaleString('fr-FR');
                const sizeMB = (b.size / 1024 / 1024).toFixed(2);
                return `<div class="backup-item">
                    <div>
                        <strong>${b.name}</strong><br>
                        <small class="text-muted">${sizeMB} MB — ${date}</small>
                    </div>
                    <button class="btn btn-green btn-xs" onclick="restoreBackup('${worldName}','${b.file}')">📥 Restaurer</button>
                </div>`;
            }).join('');
        }
    } catch(e) { alert('Erreur chargement backups'); }
}

function restoreBackup(worldName, backupFile) {
    if (!confirm('Restaurer ce backup ? Le monde actuel sera sauvegardé en sécurité.')) return;
    postAction('/restore-backup', { world_name: worldName, backup_file: backupFile });
}

async function refreshWorlds() {
    try {
        const data   = await (await fetch('/worlds')).json();
        const world  = document.getElementById('current-world');
        const select = document.getElementById('world-select');
        if (world)  world.textContent = data.current || 'Aucun';
        if (select) select.innerHTML  = data.worlds.length
            ? data.worlds.map(w => `<option value="${w.name}">${w.name} (${(w.size/1024/1024).toFixed(2)} MB)</option>`).join('')
            : '<option value="">Aucun monde disponible</option>';
    } catch(e) {}
}

/* ── Logs & statut ───────────────────────────────────────────────────────── */
const logsPre    = document.getElementById('logs');
const statusSpan = document.getElementById('status');

async function refreshLogs() {
    if (!logsPre) return;
    try {
        const logs = await (await fetch('/logs')).json();
        if (logs && logs.length > 0) {
            logsPre.textContent = logs.join('\n');
            logsPre.scrollTop   = logsPre.scrollHeight;
        }
    } catch(e) {}
}

if (logsPre)    setInterval(refreshLogs, 1000);
if (statusSpan) setInterval(async () => {
    try {
        const data = await (await fetch('/status')).json();
        statusSpan.className   = 'status ' + (data.running ? 'online' : 'offline');
        statusSpan.textContent = data.running ? '🟢 EN LIGNE' : '🔴 ARRÊTÉ';
    } catch(e) {}
}, 5000);

const cmdForm = document.querySelector('form[action="/command"]');
if (cmdForm) cmdForm.addEventListener('submit', async e => {
    e.preventDefault();
    await fetch('/command', { method: 'POST', body: new FormData(e.target) });
    e.target.reset();
    setTimeout(refreshLogs, 500);
});

/* ── Backups globaux ─────────────────────────────────────────────────────── */
async function refreshBackups() {
    const div = document.getElementById('backups');
    if (!div) return;
    try {
        const backups = await (await fetch('/backups')).json();
        div.innerHTML = backups.length
            ? backups.map(b => {
                const date   = new Date(b.date * 1000).toLocaleString('fr-FR');
                const sizeMB = (b.size / 1024 / 1024).toFixed(2);
                return `<div class="backup-item">📦 <strong>${b.name}</strong> — ${sizeMB} MB — ${date}</div>`;
              }).join('')
            : '<p class="text-muted">Aucun backup</p>';
    } catch(e) {}
}

/* ── Init dashboard ──────────────────────────────────────────────────────── */
if (document.getElementById('max-players')) {
    loadConfig();
    loadWhitelist();
    refreshWorlds();
    refreshBackups();
    setInterval(loadWhitelist,   10000);
    setInterval(refreshWorlds,   10000);
    setInterval(refreshBackups,  10000);
}

/* ══════════════════════════════════════════════════════════════════════════
   INSTALL SERVER
   ══════════════════════════════════════════════════════════════════════════ */
const installForm = document.getElementById('installForm');
if (installForm) {
    installForm.addEventListener('submit', function() {
        document.getElementById('button-group').style.display = 'none';
        document.getElementById('loading').style.display      = 'block';
    });
}

/* ══════════════════════════════════════════════════════════════════════════
   UPDATE SERVER
   ══════════════════════════════════════════════════════════════════════════ */
const updateForm = document.getElementById('updateForm');
if (updateForm) {
    updateForm.addEventListener('submit', function() {
        document.getElementById('button-group').style.display = 'none';
        document.getElementById('loading').style.display      = 'block';
    });
}

/* ── Mise à jour du manager ─────────────────────────────────── */
async function checkManagerUpdate() {
    const status  = document.getElementById("update-status");
    const actions = document.getElementById("update-actions");
    const link    = document.getElementById("update-link");
    if (!status) return;

    try {
        const data = await (await fetch("/api/updates")).json();

        if (data.status === "update_available") {
            status.innerHTML = `⚠️ <strong>Mise à jour disponible : ${data.current} → ${data.latest}</strong>`;
            if (link)    link.href = data.url;
            if (actions) actions.style.display = "flex";

        } else if (data.status === "up_to_date") {
            status.textContent = `✅ Manager à jour (${data.version})`;

        } else if (data.status === "checking") {
            status.textContent = "⏳ Vérification en cours...";

        } else {
            status.textContent = `❌ ${data.message || "Erreur vérification"}`;
        }
    } catch(e) {
        status.textContent = "❌ Erreur réseau";
    }
}

async function doManagerUpdate() {
    if (!confirm("Lancer la mise à jour du manager ?\nLe dashboard va recharger automatiquement.")) return;

    document.getElementById("update-status").textContent = "⏳ Mise à jour en cours...";
    document.getElementById("update-actions").style.display = "none";

    await fetch("/api/do-update", { method: "POST" });
    setTimeout(() => location.reload(), 8000);
}

checkManagerUpdate();
setInterval(checkManagerUpdate, 30 * 60 * 1000);
