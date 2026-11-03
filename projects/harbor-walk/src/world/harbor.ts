import * as T from "three";
import { mergeGeometries } from "three/addons/utils/BufferGeometryUtils.js";
import { PhysicsWorld } from "../physics/world";
export interface Stamp {
  id: string;
  label: string;
  position: T.Vector3;
  object: T.Group;
}
export class Harbor {
  root = new T.Group();
  obstacles: T.Object3D[] = [];
  stamps: Stamp[] = [];
  water: T.Mesh;
  lanterns: T.Mesh[] = [];
  materials = new Map<string, T.MeshStandardMaterial>();
  constructor(public physics: PhysicsWorld) {
    this.box("island", 0, -0.3, 0, 34, 0.6, 29, "#d4cab6", true);
    this.box("quay", 0, 0.015, 11.8, 34, 0.12, 1.4, "#b9a98c", true);
    this.box("walkway", 0, 0.015, 1, 27, 0.04, 17, "#c0b9a7");
    this.box("street", 0, 0.035, -3, 25, 0.035, 4.6, "#a9a798");
    // Subtle paving joints, trim stones and drain grates.
    for (let z = -10; z < 11; z += 1.15)
      for (let x = -15; x < 16; x += 2.3) {
        if ((Math.round(z * 10) + Math.round(x * 10)) % 3 === 0) continue;
        this.box("paving joint", x, 0.045, z, 2.24, 0.018, 0.014, "#aaa796");
        this.box(
          "cross joint",
          x + 1.13,
          0.045,
          z + 0.57,
          0.014,
          0.018,
          1.1,
          "#aaa796",
        );
      }
    for (let x = -15; x < 16; x += 0.75)
      this.box("quay edge", x, 0.13, 11, 0.7, 0.17, 0.34, "#eee1c5");
    this.water = new T.Mesh(
      new T.PlaneGeometry(180, 100, 30, 20),
      new T.MeshStandardMaterial({
        color: "#377c86",
        roughness: 0.28,
        metalness: 0.3,
        transparent: true,
        opacity: 0.94,
      }),
    );
    this.water.rotation.x = -Math.PI / 2;
    this.water.position.set(0, -0.22, 52);
    this.root.add(this.water);
    for (let i = 0; i < 24; i++) {
      const line = this.box(
        "water glint",
        Math.sin(i * 42) * 40,
        -0.185,
        15 + i * 2,
        2 + Math.sin(i) * 1.4,
        0.01,
        0.035,
        "#90b7ab",
      );
      line.rotation.y = Math.sin(i) * 0.12;
    }
    // Distinct authored shop fronts, arcades, window frames, awnings and rooftop detail.
    this.shop(
      -9,
      -10,
      6,
      6,
      "#d6c9ad",
      "#2c655b",
      "春日茶行",
      "TEA & SLOW DAYS",
    );
    this.shop(-2, -11, 6, 7, "#c49476", "#476867", "海風旅舍", "SEABREEZE INN");
    this.shop(5, -11, 6, 6.5, "#e4d6b8", "#436c68", "潮間書店", "TIDE BOOKS");
    this.shop(
      12,
      -9,
      5.5,
      5.6,
      "#b1bbb0",
      "#a36650",
      "港口製作所",
      "HARBOR STUDIO",
    );
    this.shop(
      -14,
      -2,
      4.4,
      5.5,
      "#dcc6a4",
      "#b06650",
      "日常食堂",
      "DAILY KITCHEN",
    );
    for (const [x, z] of [
      [-8, 5],
      [10, 5],
      [-11, -4],
      [12, -3],
    ])
      this.tree(x, z);
    this.planter(-8, 5, 3.2, 2.1);
    this.planter(10, 5, 3.2, 2.1);
    this.bench(-6, 6.7);
    this.bench(7.5, 6.7);
    this.bench(-7, -6, Math.PI);
    this.bench(10, -5.7, Math.PI);
    for (let x = -14; x <= 14; x += 4) {
      this.post(x, 10.4);
    }
    for (let i = 0; i < 12; i++) {
      const x = -13 + i * 2.4;
      const z = -1.7;
      const y = 4.6 - Math.sin((i / 11) * Math.PI) * 0.7;
      this.cylinder("lantern rib", x, y, z, 0.16, 0.24, "#d4aa68", 12);
      const l = new T.Mesh(
        new T.SphereGeometry(0.24, 12, 8),
        new T.MeshStandardMaterial({
          color: "#eac699",
          emissive: "#e6a65f",
          emissiveIntensity: 0.23,
          roughness: 0.7,
        }),
      );
      l.scale.set(1, 1.2, 1);
      l.position.set(x, y, z);
      this.root.add(l);
      this.lanterns.push(l);
      if (i < 11)
        this.beam(
          new T.Vector3(x, y + 0.3, z),
          new T.Vector3(
            x + 2.4,
            4.6 - Math.sin(((i + 1) / 11) * Math.PI) * 0.7 + 0.3,
            z,
          ),
          0.012,
          "#4c5950",
        );
    }
    // Bicycle rack and a small hand-built market stand.
    this.market(4, 2.5);
    this.bicycle(-10.8, -6.5);
    this.box("garden wall", 14, 0.3, 4, 1, 0.6, 6, "#a8a995", true);
    for (let i = 0; i < 6; i++) this.grass(14, 1.9 + i * 0.6);
    // Solid world limits; sea and houses are never traversable.
    this.physics.box(0, 1, 12, 35, 2, 0.4);
    this.physics.box(-17, 1, 0, 0.4, 2, 30);
    this.physics.box(17, 1, 0, 0.4, 2, 30);
    this.physics.box(0, 1, -14.5, 35, 2, 0.4);
    this.stamp("tea", "茶香印記", -5.5, -4.8);
    this.stamp("pier", "海風印記", 8, 8);
    this.stamp("garden", "樹影印記", -6, 3.6);
    const board = this.sign(
      "海風里  /  SEABREEZE QUARTER",
      5.6,
      0.65,
      "#264d47",
      "#eee2bc",
    );
    board.position.set(0, 0.7, 10.8);
    board.rotation.y = Math.PI;
    this.root.add(board);
    // Hazy islands on the horizon, with soft layered contours.
    for (let i = 0; i < 7; i++) {
      const m = new T.Mesh(
        new T.SphereGeometry(1, 24, 12),
        this.material("#789b96"),
      );
      m.scale.set(14 + i * 2, 2 + Math.sin(i) * 1.5, 8);
      m.position.set(-55 + i * 20, -1, 61 + Math.sin(i) * 7);
      this.root.add(m);
    }
    this.batchStatic();
  }
  batchStatic() {
    // Merge static geometry by shared material; keep original obstacle world matrices for raycasts.
    this.root.updateMatrixWorld(true);
    const groups = new Map<T.Material, T.Mesh[]>();
    for (const o of [...this.root.children]) {
      if (
        !(o instanceof T.Mesh) ||
        o === this.water ||
        this.lanterns.includes(o)
      )
        continue;
      const mat = o.material as T.Material;
      if (!groups.has(mat)) groups.set(mat, []);
      groups.get(mat)!.push(o);
    }
    for (const [material, meshes] of groups) {
      if (meshes.length < 2) continue;
      const geometries = meshes.map((m) =>
        m.geometry.clone().applyMatrix4(m.matrixWorld),
      );
      const merged = mergeGeometries(geometries, false);
      geometries.forEach((g) => g.dispose());
      if (!merged) throw new Error("Static batching geometry mismatch");
      const batch = new T.Mesh(merged, material);
      batch.name = "Static material batch";
      batch.castShadow = true;
      batch.receiveShadow = true;
      meshes.forEach((m) => {
        this.root.remove(m);
        if (!this.obstacles.includes(m)) m.geometry.dispose();
      });
      this.root.add(batch);
    }
  }
  material(color: string, roughness = 0.85, metalness = 0) {
    const key = `${color}:${roughness}:${metalness}`;
    if (!this.materials.has(key))
      this.materials.set(
        key,
        new T.MeshStandardMaterial({ color, roughness, metalness }),
      );
    return this.materials.get(key)!;
  }
  box(
    name: string,
    x: number,
    y: number,
    z: number,
    w: number,
    h: number,
    d: number,
    color: string,
    solid = false,
  ) {
    const mesh = new T.Mesh(new T.BoxGeometry(w, h, d), this.material(color));
    mesh.name = name;
    mesh.position.set(x, y, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    this.root.add(mesh);
    if (solid) {
      this.physics.box(x, y, z, w, h, d);
      this.obstacles.push(mesh);
    }
    return mesh;
  }
  cylinder(
    name: string,
    x: number,
    y: number,
    z: number,
    r: number,
    h: number,
    color: string,
    segments = 12,
  ) {
    const m = new T.Mesh(
      new T.CylinderGeometry(r, r, h, segments),
      this.material(color),
    );
    m.name = name;
    m.position.set(x, y, z);
    m.castShadow = true;
    m.receiveShadow = true;
    this.root.add(m);
    return m;
  }
  beam(a: T.Vector3, b: T.Vector3, r: number, color: string) {
    const c = a.clone().add(b).multiplyScalar(0.5);
    const m = this.cylinder(
      "beam",
      c.x,
      c.y,
      c.z,
      r,
      a.distanceTo(b),
      color,
      8,
    );
    m.quaternion.setFromUnitVectors(
      new T.Vector3(0, 1, 0),
      b.clone().sub(a).normalize(),
    );
    return m;
  }
  sign(text: string, w: number, h: number, bg: string, fg: string) {
    const c = document.createElement("canvas");
    c.width = 1024;
    c.height = 256;
    const ctx = c.getContext("2d")!;
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, 1024, 256);
    ctx.strokeStyle = fg;
    ctx.lineWidth = 3;
    ctx.strokeRect(18, 18, 988, 220);
    ctx.fillStyle = fg;
    ctx.font = `500 ${text.length > 20 ? 46 : 72}px "Noto Sans CJK TC", sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 512, 132, 940);
    const tex = new T.CanvasTexture(c);
    tex.colorSpace = T.SRGBColorSpace;
    return new T.Mesh(
      new T.PlaneGeometry(w, h),
      new T.MeshStandardMaterial({ map: tex, roughness: 0.9 }),
    );
  }
  shop(
    x: number,
    z: number,
    w: number,
    h: number,
    wall: string,
    trim: string,
    title: string,
    sub: string,
    rot = 0,
  ) {
    const start = this.root.children.length;
    const parts: T.Object3D[] = [];
    const body = this.box(title, x, h / 2, z, w, h, 4, wall, true);
    this.box("stone plinth", x, 0.2, z + 2.04, w + 0.12, 0.4, 0.22, "#aca792");
    for (let side = -1; side <= 1; side += 2)
      this.box(
        "corner column",
        x + side * (w / 2 - 0.14),
        h / 2,
        z + 2.08,
        0.25,
        h,
        0.2,
        "#e7dbc0",
      );
    const fascia = this.sign(title, w - 0.5, 0.62, trim, "#eee2bd");
    fascia.position.set(x, 2.9, z + 2.16);
    this.root.add(fascia);
    const subtitle = this.sign(sub, w - 0.8, 0.23, "#ded2b8", "#526359");
    subtitle.position.set(x, 2.44, z + 2.14);
    this.root.add(subtitle);
    for (let i = 0; i < 3; i++) {
      const wx = x - w * 0.32 + i * w * 0.32;
      this.box(
        "shop door frame",
        wx,
        1.27,
        z + 2.1,
        w * 0.29,
        2.15,
        0.15,
        trim,
      );
      this.box(
        "shop window",
        wx,
        1.31,
        z + 2.19,
        w * 0.25,
        1.8,
        0.06,
        "#65847d",
      );
      this.box(
        "window mullion",
        wx,
        1.31,
        z + 2.23,
        0.06,
        1.8,
        0.04,
        "#d2c4a6",
      );
      this.box(
        "window rail",
        wx,
        1.15,
        z + 2.24,
        w * 0.25,
        0.055,
        0.04,
        "#d2c4a6",
      );
      for (let k = 0; k < 3; k++)
        this.box(
          "upper window ledge",
          wx,
          4 + k * 0.34,
          z + 2.12,
          w * 0.24,
          0.06,
          0.1,
          trim,
        );
      this.box(
        "upper window recess",
        wx,
        4.38,
        z + 2.08,
        w * 0.26,
        1.4,
        0.16,
        trim,
      );
      this.box(
        "upper glass",
        wx,
        4.38,
        z + 2.18,
        w * 0.21,
        1.23,
        0.03,
        "#72948d",
      );
      this.box(
        "upper mullion",
        wx,
        4.38,
        z + 2.2,
        0.055,
        1.23,
        0.03,
        "#e1d6bc",
      );
    }
    this.box("balcony base", x, 3.57, z + 2.25, w - 0.45, 0.15, 0.8, trim);
    for (let bx = x - w / 2 + 0.5; bx < x + w / 2 - 0.3; bx += 0.35)
      this.box("balustrade", bx, 3.9, z + 2.62, 0.04, 0.65, 0.04, trim);
    this.box("handrail", x, 4.22, z + 2.62, w - 0.45, 0.055, 0.08, trim);
    for (let a = 0; a < 10; a++) {
      const aw = this.box(
        "striped canvas awning",
        x - w / 2 + w / 20 + (a * w) / 10,
        2.57,
        z + 2.65,
        w / 10,
        0.08,
        1.3,
        a % 2 ? "#eee1bc" : trim,
      );
      aw.rotation.x = 0.22;
      this.box(
        "awning valance",
        x - w / 2 + w / 20 + (a * w) / 10,
        2.41,
        z + 3.27,
        w / 10,
        0.23,
        0.04,
        a % 2 ? "#eee1bc" : trim,
      );
    }
    this.box("roof cornice", x, h - 0.03, z, w + 0.48, 0.2, 4.4, trim);
    for (let r = 0; r < 15; r++) {
      const zz = z - 2 + r * 0.3;
      const yy = h + 0.15 + Math.sin((r / 14) * Math.PI) * 0.45;
      this.box("roof tile course", x, yy, zz, w + 0.58, 0.12, 0.34, trim);
    }
    this.box("roof ridge", x, h + 0.63, z, w + 0.65, 0.12, 0.15, "#d1c2a5");
    this.box(
      "roof chimney",
      x + w * 0.28,
      h + 0.55,
      z - 0.9,
      0.42,
      0.9,
      0.5,
      "#d1c0a3",
    );
    void body;
  }
  planter(x: number, z: number, w: number, d: number) {
    this.box("raised planter", x, 0.22, z, w, 0.44, d, "#c2b798", true);
    this.box("earth", x, 0.45, z, w - 0.2, 0.04, d - 0.2, "#666c4c");
    for (let i = 0; i < 9; i++)
      this.grass(x + Math.sin(i * 8) * w * 0.4, z + Math.cos(i * 9) * d * 0.4);
  }
  grass(x: number, z: number) {
    for (let k = 0; k < 3; k++) {
      const m = new T.Mesh(
        new T.ConeGeometry(0.1, 0.42, 5),
        this.material(k % 2 ? "#798551" : "#96a36d"),
      );
      m.position.set(x + (k - 1) * 0.1, 0.63, z);
      m.rotation.z = (k - 1) * 0.3;
      this.root.add(m);
    }
  }
  tree(x: number, z: number) {
    this.cylinder("tree trunk", x, 1.65, z, 0.15, 3.3, "#796b50");
    this.physics.box(x, 1.6, z, 0.4, 3.2, 0.4);
    for (let i = 0; i < 9; i++) {
      const a = i * 2.4;
      const px = x + Math.sin(a) * (0.4 + i * 0.07),
        pz = z + Math.cos(a) * (0.4 + i * 0.07),
        y = 3.1 + Math.sin(i * 3) * 0.5;
      const m = new T.Mesh(
        new T.IcosahedronGeometry(1.05, 1),
        this.material(["#6f865a", "#809361", "#97a36b"][i % 3]),
      );
      m.position.set(px, y, pz);
      m.scale.set(1, 1.1, 1);
      m.castShadow = true;
      this.root.add(m);
      this.beam(
        new T.Vector3(x, 1.8, z),
        new T.Vector3(px, y, pz),
        0.045,
        "#796b50",
      );
    }
  }
  bench(x: number, z: number, rot = 0) {
    const start = this.root.children.length;
    for (let i = 0; i < 5; i++)
      this.box(
        "timber seat",
        x,
        0.48,
        z + (i - 2) * 0.11,
        1.9,
        0.08,
        0.09,
        "#947958",
      );
    for (let i = 0; i < 3; i++)
      this.box(
        "bench back",
        x,
        0.75 + i * 0.13,
        z + 0.28,
        1.9,
        0.1,
        0.07,
        "#947958",
      );
    for (const s of [-0.7, 0.7])
      this.box("cast iron leg", x + s, 0.28, z, 0.06, 0.5, 0.55, "#344d46");
    this.physics.box(x, 0.55, z, 2, 1, 0.7);
    if (rot)
      for (const o of this.root.children.slice(start)) {
        o.position.x = 2 * x - o.position.x;
        o.position.z = 2 * z - o.position.z;
        o.rotation.y = rot;
      }
  }
  post(x: number, z: number) {
    this.cylinder("bollard", x, 0.45, z, 0.12, 0.9, "#586b62");
    this.cylinder("bollard cap", x, 0.91, z, 0.16, 0.08, "#b1b49a");
    if (x < 14)
      this.beam(
        new T.Vector3(x, 0.7, z),
        new T.Vector3(x + 4, 0.7, z),
        0.025,
        "#7a8270",
      );
  }
  market(x: number, z: number) {
    this.box("market counter", x, 0.65, z, 2.4, 1.3, 1.1, "#567a65", true);
    for (let i = 0; i < 8; i++)
      this.box(
        "counter boards",
        x - 1.08 + i * 0.3,
        0.65,
        z + 0.56,
        0.02,
        1.2,
        0.02,
        "#a2ad87",
      );
    for (const dx of [-1.05, 1.05])
      this.cylinder("stall post", x + dx, 1.5, z, 0.035, 3, "#9b845e");
    for (let i = 0; i < 8; i++) {
      const a = this.box(
        "stall canopy",
        x - 1.14 + i * 0.325,
        2.65,
        z,
        0.325,
        0.08,
        1.8,
        i % 2 ? "#d5b788" : "#e7d8b3",
      );
      a.rotation.x = 0.12;
    }
    for (let i = 0; i < 12; i++) {
      const m = new T.Mesh(
        new T.SphereGeometry(0.12, 8, 6),
        this.material(i % 3 ? "#d1a34e" : "#89a265"),
      );
      m.position.set(
        x - 0.8 + (i % 6) * 0.3,
        1.4,
        z - 0.2 + Math.floor(i / 6) * 0.3,
      );
      this.root.add(m);
    }
    const s = this.sign(
      "小日子  /  LOCAL GOODS",
      2,
      0.38,
      "#567a65",
      "#f2e6c5",
    );
    s.position.set(x, 1.1, z + 0.57);
    this.root.add(s);
  }
  bicycle(x: number, z: number) {
    for (const dx of [-0.6, 0.6]) {
      const m = new T.Mesh(
        new T.TorusGeometry(0.35, 0.035, 8, 24),
        this.material("#394b45"),
      );
      m.position.set(x + dx, 0.4, z);
      this.root.add(m);
    }
    for (const [a, b] of [
      [
        [x - 0.6, 0.4, z],
        [x, 0.55, z],
      ],
      [
        [x, 0.55, z],
        [x + 0.3, 1.03, z],
      ],
      [
        [x + 0.3, 1.03, z],
        [x + 0.6, 0.4, z],
      ],
      [
        [x - 0.6, 0.4, z],
        [x - 0.25, 1, z],
      ],
      [
        [x - 0.25, 1, z],
        [x + 0.3, 1.03, z],
      ],
    ])
      this.beam(new T.Vector3(...a), new T.Vector3(...b), 0.025, "#bc8660");
    this.box("bike saddle", x - 0.25, 1.06, z, 0.25, 0.06, 0.15, "#48574b");
  }
  stamp(id: string, label: string, x: number, z: number) {
    const group = new T.Group();
    group.position.set(x, 0.8, z);
    const ring = new T.Mesh(
      new T.TorusGeometry(0.24, 0.025, 8, 32),
      new T.MeshStandardMaterial({
        color: "#f3ce78",
        emissive: "#d6a653",
        emissiveIntensity: 0.35,
      }),
    );
    const center = new T.Mesh(
      new T.OctahedronGeometry(0.17),
      this.material("#efc26c", 0.3, 0.3),
    );
    group.add(ring, center);
    this.root.add(group);
    this.stamps.push({
      id,
      label,
      position: new T.Vector3(x, 0, z),
      object: group,
    });
  }
  update(time: number) {
    this.stamps.forEach((s, i) => {
      s.object.position.y = 0.9 + Math.sin(time * 2 + i) * 0.12;
      s.object.rotation.y = time * 0.7;
    });
  }
}
