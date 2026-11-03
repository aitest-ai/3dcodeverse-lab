export class Input {
  keys = new Set<string>();
  pressed = new Set<string>();
  dragging = false;
  lookX = 0;
  lookY = 0;
  zoom = 0;
  constructor(canvas: HTMLCanvasElement) {
    window.addEventListener("keydown", (e) => {
      if (
        ["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(
          e.code,
        )
      )
        e.preventDefault();
      if (!e.repeat) this.pressed.add(e.code);
      this.keys.add(e.code);
    });
    window.addEventListener("keyup", (e) => this.keys.delete(e.code));
    window.addEventListener("blur", () => this.clear());
    canvas.addEventListener("pointerdown", (e) => {
      this.dragging = true;
      canvas.setPointerCapture(e.pointerId);
    });
    canvas.addEventListener("pointerup", () => {
      this.dragging = false;
    });
    canvas.addEventListener("pointermove", (e) => {
      if (this.dragging) {
        this.lookX += e.movementX;
        this.lookY += e.movementY;
      }
    });
    canvas.addEventListener(
      "wheel",
      (e) => {
        this.zoom += e.deltaY;
        e.preventDefault();
      },
      { passive: false },
    );
    canvas.addEventListener("contextmenu", (e) => e.preventDefault());
  }
  down(...keys: string[]) {
    return keys.some((k) => this.keys.has(k));
  }
  consume(key: string) {
    const on = this.pressed.has(key);
    this.pressed.delete(key);
    return on;
  }
  clear() {
    this.keys.clear();
    this.pressed.clear();
    this.dragging = false;
  }
  endFrame() {
    this.lookX = this.lookY = this.zoom = 0;
    this.pressed.clear();
  }
}
