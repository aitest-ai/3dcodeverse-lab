import { PerspectiveCamera, Vector3 } from "three";
import { Quest } from "../gameplay/quest";
import { NPC } from "../npc/npc";
import { Stamp } from "../world/harbor";
export const el = <T extends HTMLElement = HTMLElement>(id: string) =>
  document.getElementById(id) as T;
export const formatTime = (t: number) =>
  `${Math.floor(t / 60)
    .toString()
    .padStart(2, "0")}:${Math.floor(t % 60)
    .toString()
    .padStart(2, "0")}`;
export class HUD {
  toastUntil = 0;
  dialogue = false;
  completion = false;
  started = false;
  labels = new Map<string, HTMLDivElement>();
  constructor(public quest: Quest) {
    el("help").onclick = () =>
      (el("help-panel").hidden = !el("help-panel").hidden);
    el("close-dialogue").onclick = () => this.close();
    el("continue").onclick = () => {
      this.completion = false;
      el("completion").hidden = true;
    };
  }
  toast(text: string) {
    el("toast").textContent = text;
    el("toast").classList.add("visible");
    this.toastUntil = performance.now() + 2800;
  }
  close() {
    this.dialogue = false;
    el("dialogue").hidden = true;
  }
  start() {
    this.started = true;
    el("intro").hidden = true;
    el("mission").hidden = false;
  }
  talk(npc: NPC) {
    this.dialogue = true;
    el("dialogue").hidden = false;
    el("dialogue-role").textContent = npc.role;
    el("dialogue-name").textContent = npc.name;
    const options = el("dialogue-options");
    options.replaceChildren();
    const option = (label: string, action: () => void, secondary = false) => {
      const b = document.createElement("button");
      b.textContent = label;
      b.className = secondary ? "secondary" : "";
      b.onclick = action;
      options.append(b);
    };
    if (npc.id === "guide") {
      if (this.quest.state === "available") {
        el("dialogue-text").textContent =
          "歡迎來到海風里。我想替書店的阿青做一份街區手帖。能幫我收集茶行、榕樹與港邊的三枚印記，再親手交給她嗎？";
        option("好，交給我吧", () => {
          if (this.quest.accept())
            this.toast("委託已接下 · 跟著地圖找尋三枚印記");
          this.close();
        });
        option("我想再逛逛", () => this.close(), true);
      } else {
        el("dialogue-text").textContent =
          this.quest.state === "complete"
            ? "阿青收到手帖了嗎？謝謝你。海風里隨時歡迎你回來。"
            : "慢慢來，不用趕。茶行在北邊，榕樹就在廣場，最後記得去海堤走走。";
        option("知道了，謝謝", () => this.close());
      }
    } else {
      if (this.quest.state === "deliver") {
        el("dialogue-text").textContent =
          "是阿澄請你送來的？茶香、樹影，還有海風……這正是海風里的日常。謝謝你把這些小風景帶給我。";
        option("交付散策手帖", () => {
          if (this.quest.deliver()) {
            this.close();
            this.completion = true;
            el("completion").hidden = false;
            el("result-time").textContent = formatTime(this.quest.elapsed);
            npc.celebrate = 3;
            this.toast("委託完成 · +75 旅途點數");
          }
        });
      } else {
        el("dialogue-text").textContent =
          this.quest.state === "complete"
            ? "手帖會一直放在店裡，下次再來坐坐吧。"
            : "你好，我是阿青。書裡有遠方，街角也有風景。阿澄常在廣場散步，或許你們會聊得來。";
        option("下次來看書", () => this.close());
      }
    }
  }
  update(
    player: Vector3,
    npcs: NPC[],
    stamps: Stamp[],
    camera: PerspectiveCamera,
    nearest: NPC | undefined,
  ) {
    if (performance.now() > this.toastUntil)
      el("toast").classList.remove("visible");
    el("objective").textContent = this.quest.instruction;
    el("score").textContent = String(this.quest.score).padStart(3, "0");
    el("elapsed").textContent = formatTime(this.quest.elapsed);
    el("quest-step").textContent = {
      available: "01 / 03",
      collecting: "02 / 03",
      deliver: "03 / 03",
      complete: "完成",
    }[this.quest.state];
    document
      .querySelectorAll<HTMLElement>("[data-stamp]")
      .forEach((e) =>
        e.classList.toggle(
          "collected",
          this.quest.collected.has(e.dataset.stamp!),
        ),
      );
    el("interact").hidden =
      !this.started || this.dialogue || this.completion || !nearest;
    if (nearest)
      el("interact").querySelector("span")!.textContent =
        `與${nearest.name}聊聊`;
    for (const n of npcs) {
      let label = this.labels.get(n.id);
      if (!label) {
        label = document.createElement("div");
        label.className = "npc-label";
        label.innerHTML = `<small>${n.role}</small><b>${n.name}</b>`;
        el("npc-labels").append(label);
        this.labels.set(n.id, label);
      }
      const p = n.character.root.position
        .clone()
        .add(new Vector3(0, 2.18, 0))
        .project(camera);
      label.hidden =
        p.z > 1 ||
        p.z < -1 ||
        Math.abs(p.x) > 1.1 ||
        Math.abs(p.y) > 1.1 ||
        player.distanceTo(n.character.root.position) > 16 ||
        !this.started;
      label.style.left = `${(p.x * 0.5 + 0.5) * window.innerWidth}px`;
      label.style.top = `${(-p.y * 0.5 + 0.5) * window.innerHeight}px`;
    }
    this.map(player, npcs, stamps);
  }
  map(player: Vector3, npcs: NPC[], stamps: Stamp[]) {
    const c = el<HTMLCanvasElement>("minimap");
    const ctx = c.getContext("2d")!;
    ctx.clearRect(0, 0, c.width, c.height);
    const project = (p: Vector3) => ({ x: 120 + p.x * 6, y: 92 + p.z * 6 });
    ctx.fillStyle = "#e5e1cf";
    ctx.fillRect(7, 5, 226, 164);
    ctx.fillStyle = "#a9c4ba";
    ctx.fillRect(7, 169, 226, 25);
    ctx.fillStyle = "#b7bba2";
    for (const [x, z, w] of [
      [-9, -10, 6],
      [-2, -11, 6],
      [5, -11, 6],
      [12, -9, 5.5],
      [-14, -2, 4.4],
    ]) {
      const p = project(new Vector3(x, 0, z));
      ctx.fillRect(p.x - w * 3, p.y - 11, w * 6, 23);
    }
    ctx.strokeStyle = "#d3d2be";
    ctx.lineWidth = 17;
    ctx.beginPath();
    ctx.moveTo(10, 75);
    ctx.lineTo(230, 75);
    ctx.stroke();
    for (const s of stamps) {
      if (this.quest.collected.has(s.id) || this.quest.state === "available")
        continue;
      const p = project(s.position);
      ctx.fillStyle = "#bc9350";
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(Math.PI / 4);
      ctx.fillRect(-3, -3, 6, 6);
      ctx.restore();
    }
    for (const n of npcs) {
      const p = project(n.character.root.position);
      ctx.strokeStyle = n.id === "guide" ? "#788f72" : "#487567";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.stroke();
    }
    const p = project(player);
    ctx.fillStyle = "#24594a";
    ctx.beginPath();
    ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#fff5d9";
    ctx.lineWidth = 1.8;
    ctx.stroke();
  }
}
