import "./ui/style.css";
import { Game } from "./core/game";
import { el } from "./ui/hud";
async function boot() {
  try {
    const game = new Game();
    await game.load();
  } catch (error) {
    console.error(error);
    el("loading").hidden = false;
    el("load-status").textContent =
      `載入失敗：${error instanceof Error ? error.message : String(error)}`;
    el("retry").hidden = false;
  }
}
el("retry").onclick = () => location.reload();
boot();
