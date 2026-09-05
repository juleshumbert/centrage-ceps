/* ───────────────────────────────────────────────────────────────────────────
   auth.js — Portail d'accès partagé pour briefing.ceps09.com
   ---------------------------------------------------------------------------
   Porte le modèle d'authentification des apps sœurs (planning-app, manex-ceps09)
   en vanilla JS pour ce site statique multi-pages :
     • même projet Firebase  : paraclub-planning-f966c
     • même collection users/{uid} : l'appartenance = posséder un doc user
       (sinon « compte non autorisé »). Création invitation-only via planning-app.
     • allowlist admin : auto-bootstrap du doc (rôle admin) au 1er login.

   Chaque page charge ce module dans <head> ; il masque le contenu tant que
   l'accès n'est pas confirmé (cf. le garde inline `auth-pending` dans chaque page).
   Aucune règle Firestore n'est gérée ici : elles vivent dans planning-app et sont
   partagées par tout le projet.
   ─────────────────────────────────────────────────────────────────────────── */

const FB_VERSION = "11.10.0"; // doit matcher la version du SDK utilisée par briefing-demi-journee.html

const FIREBASE_CONFIG = {
  apiKey: "AIzaSyDX0hKKsX_eVVhbt8-gtDfFn1XFohWdlC8",
  authDomain: "paraclub-planning-f966c.firebaseapp.com",
  projectId: "paraclub-planning-f966c",
  storageBucket: "paraclub-planning-f966c.firebasestorage.app",
  messagingSenderId: "654361202662",
  appId: "1:654361202662:web:a18be0b9d3c6d023c69027",
};

// Allowlist admin — doit refléter planning-app/frontend/src/config.ts + firestore.rules.
const ADMIN_EMAILS = ["jules.humbert@gmail.com", "admin@paraclub.app"];
const isAdminEmail = (email) => !!email && ADMIN_EMAILS.includes(email.toLowerCase());

const reveal = () => document.documentElement.classList.remove("auth-pending");

// ── Imports SDK (ESM gstatic, même CDN/version que le reste du site) ──────────
const base = `https://www.gstatic.com/firebasejs/${FB_VERSION}/`;
const [appMod, authMod, fsMod] = await Promise.all([
  import(base + "firebase-app.js"),
  import(base + "firebase-auth.js"),
  import(base + "firebase-firestore.js"),
]);

const app = appMod.getApps && appMod.getApps().length ? appMod.getApp() : appMod.initializeApp(FIREBASE_CONFIG);
const auth = authMod.getAuth(app);
const db = fsMod.getFirestore(app);
const googleProvider = new authMod.GoogleAuthProvider();

// ── SSO du portail pilote (pilot.ceps09.com) ─────────────────────────────────
// Le portail passe un jeton custom éphémère dans le fragment (#sso=…) pour
// propager ici la session déjà ouverte là-bas. Consommé puis retiré de l'URL
// aussitôt (le fragment n'est jamais envoyé au serveur) ; en cas d'échec
// (jeton expiré…), le flux normal — session locale ou écran de connexion —
// reprend simplement.
const ssoMatch = location.hash.match(/[#&]sso=([^&]+)/);
if (ssoMatch) {
  history.replaceState(null, "", location.pathname + location.search);
  try { await authMod.signInWithCustomToken(auth, decodeURIComponent(ssoMatch[1])); }
  catch (e) { console.warn("Jeton SSO du portail ignoré :", (e && e.code) || e); }
}

// ── Styles + DOM de l'overlay ────────────────────────────────────────────────
const css = `
#authOverlay{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;
  padding:20px;background:radial-gradient(120% 120% at 50% 0%,#13283f 0%,#0b1622 60%,#070d15 100%);
  font-family:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#e8eef5;-webkit-font-smoothing:antialiased}
#authOverlay *{box-sizing:border-box}
#authOverlay .auth-card{width:100%;max-width:392px;background:rgba(16,28,42,.92);border:1px solid rgba(120,160,200,.18);
  border-radius:16px;padding:30px 28px 24px;box-shadow:0 24px 60px rgba(0,0,0,.5)}
#authOverlay .auth-brand{display:flex;align-items:center;gap:9px;margin-bottom:4px;color:#3fb6d6;
  text-transform:uppercase;letter-spacing:.2em;font-size:.7rem;font-weight:700}
#authOverlay h1{margin:.5rem 0 .25rem;font-size:1.32rem;font-weight:700;letter-spacing:-.01em}
#authOverlay .auth-sub{margin:0 0 20px;color:#9db1c6;font-size:.86rem;line-height:1.45}
#authOverlay label{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#8aa0b6;margin:12px 0 5px;font-weight:600}
#authOverlay input{width:100%;padding:11px 13px;background:#0b1622;border:1px solid rgba(120,160,200,.24);border-radius:9px;
  color:#eef4fa;font-size:.95rem;outline:none;transition:border-color .15s}
#authOverlay input:focus{border-color:#3fb6d6}
#authOverlay .auth-btn{width:100%;margin-top:18px;padding:12px;border:none;border-radius:9px;cursor:pointer;
  font-size:.95rem;font-weight:600;font-family:inherit;transition:filter .15s,opacity .15s}
#authOverlay .auth-btn:disabled{opacity:.6;cursor:default}
#authOverlay .auth-btn.primary{background:linear-gradient(180deg,#e8a020,#d18e16);color:#1a1206}
#authOverlay .auth-btn.primary:hover:not(:disabled){filter:brightness(1.07)}
#authOverlay .auth-btn.google{background:#fff;color:#1f2937;display:flex;align-items:center;justify-content:center;gap:9px;margin-top:10px}
#authOverlay .auth-btn.google:hover:not(:disabled){filter:brightness(.96)}
#authOverlay .auth-btn.ghost{background:transparent;border:1px solid rgba(120,160,200,.3);color:#cdd9e6}
#authOverlay .auth-or{display:flex;align-items:center;gap:10px;margin:16px 0 2px;color:#6c819a;font-size:.74rem;text-transform:uppercase;letter-spacing:.1em}
#authOverlay .auth-or::before,#authOverlay .auth-or::after{content:"";flex:1;height:1px;background:rgba(120,160,200,.18)}
#authOverlay .auth-link{display:inline-block;margin-top:14px;color:#3fb6d6;font-size:.82rem;cursor:pointer;text-decoration:none;background:none;border:none;padding:0;font-family:inherit}
#authOverlay .auth-link:hover{text-decoration:underline}
#authOverlay .auth-msg{margin-top:14px;font-size:.82rem;line-height:1.4;display:none}
#authOverlay .auth-msg.error{display:block;color:#ff9a8b}
#authOverlay .auth-msg.ok{display:block;color:#86e0a8}
#authOverlay .auth-foot{margin-top:20px;padding-top:16px;border-top:1px solid rgba(120,160,200,.12);color:#6c819a;font-size:.74rem;line-height:1.5}
#authOverlay .auth-mono{font-family:'IBM Plex Mono',ui-monospace,monospace;color:#cdd9e6;word-break:break-all}
#authChip{position:fixed;right:12px;bottom:12px;z-index:2147482000;display:flex;align-items:center;gap:8px;
  padding:6px 10px;background:rgba(13,27,42,.92);border:1px solid rgba(120,160,200,.22);border-radius:999px;
  color:#cdd9e6;font:600 .74rem/1 system-ui,-apple-system,'Segoe UI',sans-serif;box-shadow:0 6px 18px rgba(0,0,0,.35)}
#authChip button{background:none;border:none;color:#ff9a8b;cursor:pointer;font:inherit;padding:0}
#authChip button:hover{text-decoration:underline}
/* Variante « intégrée » : si la page expose #authChipSlot, le chip s'y loge (statique, dans l'en-tête) au lieu de flotter au-dessus du contenu. */
#authChip.slotted{position:static;inset:auto;box-shadow:none;background:transparent;border:none;border-radius:0;padding:0;color:#5a6b7d;gap:8px}
#authChip.slotted span{max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#authChip.slotted button{color:#c0392b}
@media print{#authChip{display:none!important}}
`;
const styleEl = document.createElement("style");
styleEl.textContent = css;
document.documentElement.appendChild(styleEl);

const overlay = document.createElement("div");
overlay.id = "authOverlay";
overlay.setAttribute("role", "dialog");
overlay.setAttribute("aria-modal", "true");
document.documentElement.appendChild(overlay);

const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function showLoading(text) {
  overlay.style.display = "flex";
  overlay.innerHTML = `<div class="auth-card"><div class="auth-brand">◎ Briefing CEPS09</div>
    <h1>Accès réservé</h1><p class="auth-sub">${esc(text || "Vérification de l'accès…")}</p></div>`;
}

const GOOGLE_SVG = `<svg width="17" height="17" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>`;

function showLogin(prefillEmail) {
  overlay.style.display = "flex";
  overlay.innerHTML = `<div class="auth-card">
    <div class="auth-brand">◎ Briefing CEPS09</div>
    <h1>Connexion</h1>
    <p class="auth-sub">Accès réservé aux membres du club. Connecte-toi avec ton compte CEPS09.</p>
    <form id="authForm" autocomplete="on">
      <label for="authEmail">Adresse e-mail</label>
      <input id="authEmail" type="email" autocomplete="username" required value="${esc(prefillEmail || "")}" />
      <label for="authPwd">Mot de passe</label>
      <input id="authPwd" type="password" autocomplete="current-password" required />
      <button type="submit" class="auth-btn primary" id="authSubmit">Se connecter</button>
    </form>
    <div class="auth-or">ou</div>
    <button class="auth-btn google" id="authGoogle">${GOOGLE_SVG}<span>Continuer avec Google</span></button>
    <button class="auth-link" id="authForgot">Mot de passe oublié ?</button>
    <div class="auth-msg" id="authMsg"></div>
    <div class="auth-foot">Tu n'as pas de compte ? L'accès est géré par un administrateur du club.</div>
  </div>`;

  const form = overlay.querySelector("#authForm");
  const emailEl = overlay.querySelector("#authEmail");
  const pwdEl = overlay.querySelector("#authPwd");
  const submitBtn = overlay.querySelector("#authSubmit");
  const googleBtn = overlay.querySelector("#authGoogle");
  const msg = overlay.querySelector("#authMsg");
  const setMsg = (txt, kind) => { msg.className = "auth-msg" + (kind ? " " + kind : ""); msg.textContent = txt || ""; };
  const busy = (b) => { submitBtn.disabled = b; googleBtn.disabled = b; };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMsg(""); busy(true); submitBtn.textContent = "Connexion…";
    try {
      await authMod.signInWithEmailAndPassword(auth, emailEl.value.trim(), pwdEl.value);
      // onAuthStateChanged prend le relais.
    } catch (err) {
      busy(false); submitBtn.textContent = "Se connecter";
      setMsg(authErrorMessage(err), "error");
    }
  });

  googleBtn.addEventListener("click", async () => {
    setMsg(""); busy(true);
    try {
      await authMod.signInWithPopup(auth, googleProvider);
    } catch (err) {
      busy(false);
      setMsg(authErrorMessage(err), "error");
    }
  });

  overlay.querySelector("#authForgot").addEventListener("click", async () => {
    const email = emailEl.value.trim();
    if (!email) { setMsg("Saisis ton adresse e-mail puis reclique sur « Mot de passe oublié ? ».", "error"); emailEl.focus(); return; }
    try {
      await authMod.sendPasswordResetEmail(auth, email);
      setMsg("E-mail de réinitialisation envoyé (vérifie tes spams).", "ok");
    } catch (err) {
      setMsg(authErrorMessage(err), "error");
    }
  });

  if (!emailEl.value) emailEl.focus(); else pwdEl.focus();
}

function showNotMember(email) {
  overlay.style.display = "flex";
  overlay.innerHTML = `<div class="auth-card">
    <div class="auth-brand">◎ Briefing CEPS09</div>
    <h1>Compte non autorisé</h1>
    <p class="auth-sub">Tu es bien connecté, mais ce compte n'est pas membre du club&nbsp;:</p>
    <p class="auth-mono">${esc(email || "")}</p>
    <p class="auth-sub" style="margin-top:14px">Demande à un administrateur du CEPS09 d'ouvrir l'accès à cette adresse, puis reconnecte-toi.</p>
    <button class="auth-btn ghost" id="authLogout">Se déconnecter</button>
  </div>`;
  overlay.querySelector("#authLogout").addEventListener("click", () => authMod.signOut(auth));
}

function authErrorMessage(err) {
  const code = (err && err.code) || "";
  switch (code) {
    case "auth/invalid-email": return "Adresse e-mail invalide.";
    case "auth/user-disabled": return "Ce compte est désactivé.";
    case "auth/user-not-found":
    case "auth/wrong-password":
    case "auth/invalid-credential": return "E-mail ou mot de passe incorrect.";
    case "auth/too-many-requests": return "Trop de tentatives. Réessaie dans quelques minutes.";
    case "auth/popup-closed-by-user": return "Fenêtre Google fermée avant la fin de la connexion.";
    case "auth/popup-blocked": return "La fenêtre Google a été bloquée par le navigateur.";
    case "auth/network-request-failed": return "Problème réseau. Vérifie ta connexion.";
    default: return "Échec de la connexion" + (code ? " (" + code + ")" : "") + ".";
  }
}

function mountChip(email) {
  const slot = document.getElementById("authChipSlot");
  let chip = document.getElementById("authChip");
  if (!chip) {
    chip = document.createElement("div");
    chip.id = "authChip";
    (slot || document.documentElement).appendChild(chip);
  } else if (slot && chip.parentElement !== slot) {
    slot.appendChild(chip);
  }
  chip.classList.toggle("slotted", !!slot);
  chip.innerHTML = `<span>${esc(email || "")}</span><button type="button" id="authChipLogout" title="Se déconnecter">Déconnexion</button>`;
  chip.querySelector("#authChipLogout").addEventListener("click", () => authMod.signOut(auth));
}
function removeChip() {
  const chip = document.getElementById("authChip");
  if (chip) chip.remove();
}

// ── Machine à états : onAuthStateChanged → doc users/{uid} ────────────────────
let unsubUserDoc = null;
showLoading();

authMod.onAuthStateChanged(auth, (fbUser) => {
  if (unsubUserDoc) { unsubUserDoc(); unsubUserDoc = null; }

  if (!fbUser) {
    removeChip();
    showLogin();
    return;
  }

  showLoading("Connexion…");
  const userRef = fsMod.doc(db, "users", fbUser.uid);
  unsubUserDoc = fsMod.onSnapshot(
    userRef,
    async (snap) => {
      if (!snap.exists()) {
        // Auto-bootstrap réservé à l'allowlist admin (œuf-et-poule du 1er admin) ;
        // tout autre compte connecté sans doc → non membre.
        if (isAdminEmail(fbUser.email)) {
          try {
            await fsMod.setDoc(userRef, {
              email: fbUser.email,
              full_name: fbUser.displayName || null,
              role: "admin",
              pilot_id: null,
              active: true,
            });
            return; // onSnapshot se redéclenchera avec le nouveau doc
          } catch (e) {
            console.error("Provisioning admin doc échoué", e);
            showNotMember(fbUser.email);
            return;
          }
        }
        showNotMember(fbUser.email);
        return;
      }
      // Membre confirmé → on révèle la page.
      overlay.style.display = "none";
      overlay.innerHTML = "";
      reveal();
      mountChip(fbUser.email);
    },
    (err) => {
      console.error("Lecture du doc user échouée", err);
      showNotMember(fbUser.email);
    }
  );
});

// API minimale pour les pages (ex. bouton de déconnexion intégré).
window.briefingAuth = {
  logout: () => authMod.signOut(auth),
  currentUser: () => auth.currentUser,
  isAdminEmail,
};
