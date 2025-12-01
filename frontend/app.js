const apiBase = "http://localhost:8000";
let token = null;

const recommendedCards = document.getElementById("recommendedCards");
const dialog = document.getElementById("authDialog");
const form = document.getElementById("authForm");
const loginBtn = document.getElementById("loginBtn");
const subscribeBtn = document.getElementById("subscribeBtn");
const watchBtn = document.getElementById("watchBtn");
const closeDialog = document.getElementById("closeDialog");

loginBtn.addEventListener("click", () => dialog.showModal());
closeDialog.addEventListener("click", () => dialog.close());

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  try {
    const response = await fetch(`${apiBase}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("Falha no login");
    const data = await response.json();
    token = data.token;
    dialog.close();
    watchBtn.textContent = "Assistir (logado)";
  } catch (err) {
    alert(err.message);
  }
});

subscribeBtn.addEventListener("click", async () => {
  if (!token) {
    alert("Faça login antes de assinar.");
    return;
  }
  const payload = Object.fromEntries(new FormData(form).entries());
  try {
    const response = await fetch(`${apiBase}/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: payload.email, plan: "premium" }),
    });
    if (!response.ok) throw new Error("Não foi possível assinar");
    alert("Assinatura ativada!");
  } catch (err) {
    alert(err.message);
  }
});

watchBtn.addEventListener("click", async () => {
  if (!token) {
    dialog.showModal();
    return;
  }
  try {
    const response = await fetch(`${apiBase}/play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, title_id: "001" }),
    });
    if (!response.ok) throw new Error("Sessão não iniciada");
    const data = await response.json();
    alert(`Sessão criada! URL: ${data.url}`);
  } catch (err) {
    alert(err.message);
  }
});

async function loadCatalog() {
  try {
    const response = await fetch(`${apiBase}/catalog`);
    const items = await response.json();
    recommendedCards.innerHTML = items
      .map(
        (item) => `
        <article class="card">
          <div class="thumb" style="height: 160px; border-radius: 10px; background: linear-gradient(135deg, rgba(229,9,20,0.2), rgba(255,255,255,0.02)), url('https://picsum.photos/seed/${item.id}/400/300') center/cover"></div>
          <h3>${item.name}</h3>
          <p>${item.synopsis}</p>
        </article>
      `
      )
      .join("\n");
  } catch (err) {
    recommendedCards.innerHTML = `<p class="muted">Falha ao carregar catálogo.</p>`;
  }
}

loadCatalog();
