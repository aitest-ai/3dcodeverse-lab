/**
 * Load a HY-World 2.0 export packaged by scripts/hyworld2/pack_world.py.
 * Unlike a GLB, Gaussian splats provide appearance but no collision geometry.
 *
 * npm install three @sparkjsdev/spark
 * The host must add a SparkRenderer to the Three.js scene for splat rendering.
 */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";
import { SplatLoader, SplatMesh } from "@sparkjsdev/spark";

const SUPPORTED = new Set(["gaussian_splats", "point_cloud", "triangle_mesh", "mesh_scene"]);

/**
 * @param {string} manifestURL - public world_manifest.json URL
 * @param {THREE.Scene|THREE.Group} parent - scene for the 3D asset
 * @returns {Promise<{object:THREE.Object3D, manifest:object, collisionReady:false, dispose:()=>void}>}
 */
export async function loadHYWorld(manifestURL, parent) {
  if (!parent || typeof parent.add !== "function") {
    throw new TypeError("A THREE.Scene or Group must be passed as parent");
  }
  const response = await fetch(manifestURL);
  if (!response.ok) throw new Error("Cannot fetch HY world manifest: " + response.status);
  const manifest = await response.json();
  if (manifest.schema_version !== 1 || !SUPPORTED.has(manifest.asset_type)) {
    throw new Error("Unsupported world manifest type/version");
  }
  const filename = manifest.model_file;
  if (typeof filename !== "string" || !/^[A-Za-z0-9_-]+\.(ply|spz|glb)$/i.test(filename)) {
    throw new Error("Unsafe model filename");
  }
  const assetURL = new URL(filename, new URL(manifestURL, location.href)).href;
  const holder = new THREE.Group();
  holder.name = manifest.asset_id || "hyworld";
  // Coordinate systems are NOT universally consistent between HY outputs.
  // Unknown axis and units remain unchanged until manually calibrated.
  if (manifest.source_up_axis === "Z") holder.rotation.x = -Math.PI / 2;
  if (manifest.source_up_axis !== "Z" &&
      manifest.source_up_axis !== "Y" &&
      manifest.source_up_axis !== "unknown") {
    throw new Error("Unsupported source up axis");
  }
  const scale = manifest.meters_per_source_unit;
  if (scale != null) {
    if (!Number.isFinite(scale) || scale <= 0) throw new Error("Invalid scale");
    holder.scale.setScalar(scale);
  }

  let object = null;
  if (manifest.asset_type === "gaussian_splats") {
    if (!/\.(ply|spz)$/i.test(filename)) throw new Error("Splats need .ply/.spz");
    // Wait for the data to load before publishing the object to the scene.
    const packedSplats = await new SplatLoader().loadAsync(assetURL);
    object = new SplatMesh({ packedSplats });
  } else if (manifest.asset_type === "mesh_scene") {
    if (!/\.glb$/i.test(filename)) throw new Error("GLB required");
    object = (await new GLTFLoader().loadAsync(assetURL)).scene;
  } else {
    if (!/\.ply$/i.test(filename)) throw new Error("PLY required");
    const geometry = await new PLYLoader().loadAsync(assetURL);
    const hasColors = Boolean(geometry.getAttribute("color"));
    if (manifest.asset_type === "triangle_mesh") {
      if (!geometry.getIndex()) {
        // Some PLY loaders unpack triangular faces into vertex triples.
        if (geometry.getAttribute("position").count % 3 !== 0) {
          throw new Error("Triangle mesh missing usable faces");
        }
      }
      if (!geometry.hasAttribute("normal")) geometry.computeVertexNormals();
      object = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
        vertexColors: hasColors, color: 0xffffff, side: THREE.DoubleSide,
      }));
    } else {
      object = new THREE.Points(geometry, new THREE.PointsMaterial({
        vertexColors: hasColors, color: 0xffffff, size: 0.03, sizeAttenuation: true,
      }));
    }
  }
  holder.add(object);
  parent.add(holder);

  return {
    object: holder,
    manifest,
    collisionReady: false,
    dispose() {
      parent.remove(holder);
      object.traverse(child => {
        if (child.geometry) child.geometry.dispose();
        if (child.material) {
          for (const material of Array.isArray(child.material) ? child.material : [child.material]) {
            material.dispose();
          }
        }
      });
      // Spark GPU-managed buffers may require a renderer-specific cleanup path.
    },
  };
}
