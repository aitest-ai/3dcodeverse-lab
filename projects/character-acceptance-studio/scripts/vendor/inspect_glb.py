#!/usr/bin/env python3
"""Inspect real, decoded glTF 2.0 GLB data without Blender or third-party modules.

This is a focused binary/character-structure audit, not the complete Khronos
validator and never an art, animation-contact, browser, or device approval.
Sparse substitutions are applied to decoded base data BEFORE measurements.
External resources are never fetched or opened; embed them in the deliverable.

Reference: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html
Public API: GLB(source).accessor(index), inspect_glb(path), inspect_bytes(data),
image_dimensions(data), self_test(). Rows returned by accessor() are tuples,
including one-element tuples for SCALAR. Matrices remain column-major.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
import struct
import sys
from pathlib import Path
from urllib.parse import unquote_to_bytes

SCHEMA = "3dcodeverse.character-studio.glb-inspection/1"
VERSION = "1.0.0"
COMPONENTS = {
    5120: ("b", 1, True, 127), 5121: ("B", 1, False, 255),
    5122: ("h", 2, True, 32767), 5123: ("H", 2, False, 65535),
    5125: ("I", 4, False, 4294967295), 5126: ("f", 4, False, None),
}
SHAPES = {"SCALAR": (1, 1), "VEC2": (2, 1), "VEC3": (3, 1),
          "VEC4": (4, 1), "MAT2": (2, 2), "MAT3": (3, 3), "MAT4": (4, 4)}


class GLBError(ValueError):
    """Malformed or unsupported data; callers must not convert it into a pass."""


def _int(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise GLBError(f"{label}: expected integer >= {minimum}")
    return value


def _index(items, index, label):
    index = _int(index, label)
    if not isinstance(items, list) or index >= len(items):
        raise GLBError(f"{label}: index {index} is out of range")
    return items[index]


def _reject_constant(value):
    raise GLBError("Non-finite JSON constant: " + value)


def _json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise GLBError("JSON number exceeds finite float range")
    return number


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise GLBError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def _data_uri(uri):
    if not isinstance(uri, str) or not uri.startswith("data:") or "," not in uri:
        raise GLBError("External resources are not read; supply an embedded GLB")
    header, payload = uri.split(",", 1)
    try:
        return base64.b64decode(unquote_to_bytes(payload), validate=True) if ";base64" in header else unquote_to_bytes(payload)
    except (ValueError, base64.binascii.Error) as exc:
        raise GLBError("Invalid data URI") from exc


def _layout(kind, component):
    if kind not in SHAPES or component not in COMPONENTS:
        raise GLBError(f"Unsupported accessor layout {kind}/{component}")
    rows, columns = SHAPES[kind]
    size = COMPONENTS[component][1]
    # glTF aligns each matrix column to four bytes, including MAT2/MAT3
    # with byte/short components. Final trailing padding may be omitted.
    column_stride = ((rows * size + 3) // 4) * 4 if columns > 1 else rows * size
    offsets = [c * column_stride + r * size for c in range(columns) for r in range(rows)]
    return offsets, column_stride * columns, offsets[-1] + size


class GLB:
    def __init__(self, source, label=None):
        if isinstance(source, (bytes, bytearray, memoryview)):
            self.data = bytes(source)
            self.path = label or "<memory>"
        else:
            self.path = str(Path(source))
            self.data = Path(source).read_bytes()
        data = self.data
        if len(data) < 20:
            raise GLBError("Truncated GLB header")
        magic, version, total = struct.unpack_from("<4sII", data)
        if magic != b"glTF" or version != 2 or total != len(data):
            raise GLBError("Invalid GLB magic, version, or declared total length")
        self.chunks, self.doc, self.binary = [], None, None
        position = 12
        while position < len(data):
            if len(data) - position < 8:
                raise GLBError("Truncated GLB chunk header")
            size, kind = struct.unpack_from("<I4s", data, position)
            position += 8
            if size % 4 or position + size > len(data):
                raise GLBError("Unaligned or out-of-bounds GLB chunk")
            chunk = data[position:position + size]
            chunk_number = len(self.chunks)
            if chunk_number == 0 and kind != b"JSON":
                raise GLBError("First GLB chunk must be JSON")
            self.chunks.append({"type_hex": kind.hex(), "bytes": size, "offset": position})
            if kind == b"JSON":
                if self.doc is not None or chunk_number != 0:
                    raise GLBError("Duplicate or misplaced JSON chunk")
                try:
                    self.doc = json.loads(chunk.decode("utf-8"), parse_constant=_reject_constant, parse_float=_json_float, object_pairs_hook=_object)
                except (UnicodeError, json.JSONDecodeError) as exc:
                    raise GLBError("Invalid UTF-8 JSON chunk") from exc
            elif kind == b"BIN\0":
                if self.binary is not None or chunk_number != 1:
                    raise GLBError("Duplicate or misplaced BIN chunk")
                self.binary = chunk
            position += size
        if not isinstance(self.doc, dict) or self.doc.get("asset", {}).get("version") != "2.0":
            raise GLBError("Expected a glTF 2.0 asset object")
        self.sha256 = hashlib.sha256(data).hexdigest()
        self._buffers, self._cache = {}, {}
        # Validate buffer/view ranges even if an invalid view is never used.
        for index in range(len(self.doc.get("buffers", []))):
            self.buffer(index)
        for index in range(len(self.doc.get("bufferViews", []))):
            self.view(index)

    def buffer(self, index):
        index = _int(index, "buffer")
        if index in self._buffers:
            return self._buffers[index]
        info = _index(self.doc.get("buffers", []), index, "buffer")
        length = _int(info.get("byteLength"), "buffer.byteLength", 1)
        if "uri" in info:
            raw = _data_uri(info["uri"])
            if len(raw) < length:
                raise GLBError("Embedded URI buffer is truncated")
        else:
            if index != 0 or self.binary is None:
                raise GLBError("Missing embedded BIN buffer")
            raw = self.binary
            if not length <= len(raw) <= length + 3:
                raise GLBError("BIN length disagrees with buffer.byteLength")
            if any(raw[length:]):
                raise GLBError("BIN chunk padding must contain zero bytes")
        self._buffers[index] = raw[:length]
        return self._buffers[index]

    def view(self, index):
        info = _index(self.doc.get("bufferViews", []), index, "bufferView")
        raw = self.buffer(_int(info.get("buffer"), "bufferView.buffer"))
        start = _int(info.get("byteOffset", 0), "bufferView.byteOffset")
        length = _int(info.get("byteLength"), "bufferView.byteLength", 1)
        if start + length > len(raw):
            raise GLBError("bufferView exceeds its buffer")
        if "byteStride" in info:
            stride = _int(info["byteStride"], "bufferView.byteStride", 4)
            if stride > 252 or stride % 4:
                raise GLBError("bufferView.byteStride must be a multiple of four in [4, 252]")
        return info, memoryview(raw)[start:start + length]

    def _elements(self, view_index, offset, count, component, kind, packed=False):
        info, data = self.view(view_index)
        offset = _int(offset, "accessor byteOffset")
        offsets, element_stride, span = _layout(kind, component)
        fmt, component_size, _, _ = COMPONENTS[component]
        if offset % component_size or (info.get("byteOffset", 0) + offset) % component_size:
            raise GLBError("Accessor component alignment is invalid")
        if kind.startswith("MAT") and (info.get("byteOffset", 0) + offset) % 4:
            raise GLBError("Matrix columns must start on four-byte boundaries")
        if packed and ("byteStride" in info or "target" in info):
            raise GLBError("Sparse indices/values must use tightly packed bufferViews without target")
        stride = element_stride if packed else info.get("byteStride", element_stride)
        if stride < element_stride or stride % component_size:
            raise GLBError("Accessor stride is smaller than an element or misaligned")
        if offset + (count - 1) * stride + span > len(data):
            raise GLBError("Accessor elements exceed their bufferView")
        scalar = struct.Struct("<" + fmt)
        return [tuple(scalar.unpack_from(data, offset + row * stride + col)[0] for col in offsets) for row in range(count)]

    def accessor(self, index, normalized=True):
        """Decode full base + sparse data; normalized=False returns raw integers."""
        index = _int(index, "accessor")
        key = (index, bool(normalized))
        if key in self._cache:
            return self._cache[key]
        a = _index(self.doc.get("accessors", []), index, "accessor")
        count = _int(a.get("count"), "accessor.count", 1)
        component = a.get("componentType")
        offsets, _, _ = _layout(a.get("type"), component)
        if not isinstance(a.get("normalized", False), bool):
            raise GLBError("accessor.normalized must be boolean")
        if a.get("normalized") and component not in (5120, 5121, 5122, 5123):
            raise GLBError("Only byte/short component types may be normalized")
        raw_key = (index, False)
        if raw_key in self._cache:
            rows = self._cache[raw_key]
        else:
            if "bufferView" in a:
                rows = self._elements(a["bufferView"], a.get("byteOffset", 0), count, component, a["type"])
            else:
                if "byteOffset" in a:
                    raise GLBError("An implicit-zero accessor cannot have byteOffset")
                rows = [(0,) * len(offsets)] * count
            if "sparse" in a:
                sparse = a["sparse"]
                n = _int(sparse.get("count"), "sparse.count", 1)
                if n > count:
                    raise GLBError("Sparse count exceeds accessor count")
                indices, values = sparse.get("indices", {}), sparse.get("values", {})
                ct = indices.get("componentType")
                if ct not in (5121, 5123, 5125):
                    raise GLBError("Sparse indices must be unsigned byte, short, or int")
                ids = self._elements(indices.get("bufferView"), indices.get("byteOffset", 0), n, ct, "SCALAR", packed=True)
                ids = [row[0] for row in ids]
                if any(i >= count for i in ids) or any(b <= a for a, b in zip(ids, ids[1:])):
                    raise GLBError("Sparse indices must be in range and strictly increasing")
                replacements = self._elements(values.get("bufferView"), values.get("byteOffset", 0), n, component, a["type"], packed=True)
                for i, value in zip(ids, replacements):
                    rows[i] = value
            self._cache[raw_key] = rows
        if normalized and a.get("normalized"):
            _, _, signed, maximum = COMPONENTS[component]
            rows = [tuple(max(v / maximum, -1.0) if signed else v / maximum for v in row) for row in rows]
        self._cache[key] = rows
        return rows

    read_accessor = accessor

    def image_bytes(self, index):
        info = _index(self.doc.get("images", []), index, "image")
        if "bufferView" in info and "uri" in info:
            raise GLBError("Image cannot contain both bufferView and uri")
        if "bufferView" in info:
            return bytes(self.view(info["bufferView"])[1])
        return _data_uri(info.get("uri"))


def image_dimensions(data):
    """Return PNG/JPEG dimensions from headers; this does NOT decode pixels."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        if len(data) < 33 or data[12:16] != b"IHDR" or struct.unpack_from(">I", data, 8)[0] != 13:
            raise GLBError("Invalid PNG IHDR")
        width, height = struct.unpack_from(">II", data, 16)
        kind = "PNG"
    elif data.startswith(b"\xff\xd8"):
        position, width, height = 2, None, None
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while position < len(data):
            if data[position] != 0xFF:
                raise GLBError("Invalid JPEG marker stream")
            while position < len(data) and data[position] == 0xFF:
                position += 1
            if position >= len(data):
                break
            marker = data[position]
            position += 1
            if marker in (0xD9, 0xDA):
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD7:
                continue
            if position + 2 > len(data):
                raise GLBError("Truncated JPEG marker")
            length = struct.unpack_from(">H", data, position)[0]
            if length < 2 or position + length > len(data):
                raise GLBError("Truncated JPEG segment")
            if marker in sof:
                if length < 8:
                    raise GLBError("Invalid JPEG SOF")
                height, width = struct.unpack_from(">HH", data, position + 3)
                break
            position += length
        if width is None:
            raise GLBError("JPEG has no supported SOF dimensions")
        kind = "JPEG"
    else:
        raise GLBError("Image header is neither PNG nor JPEG")
    if not width or not height:
        raise GLBError("Image dimensions must be positive")
    return {"format": kind, "width": width, "height": height, "verification": "header_only_not_pixel_decode"}


def _finite(values):
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in values)


def _bounds(rows):
    good = [row for row in rows if _finite(row)]
    if not good:
        return {"min": None, "max": None}
    return {"min": [min(c) for c in zip(*good)], "max": [max(c) for c in zip(*good)]}


def _det3(matrix):
    # Input is glTF column-major MAT4.
    a, b, c, d, e, f, g, h, i = (matrix[j] for j in (0, 4, 8, 1, 5, 9, 2, 6, 10))
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _bone_key(name):
    name = name.rsplit(":", 1)[-1].rsplit("|", 1)[-1].lower()
    name = re.sub(r"^(mixamorig|def[-_])", "", name)
    return re.sub(r"[^a-z0-9]", "", name)


SEMANTIC_ALIASES = {
    "root": {"root", "rootmotion"}, "pelvis": {"pelvis", "hips", "hip"},
    "spine_lower": {"spine", "spine01", "spine1"},
    "spine_middle": {"spine02", "spine2", "chest"},
    "spine_upper": {"spine03", "spine3", "upperchest"},
    "neck": {"neck", "neck01"}, "head": {"head"},
}
for _side, _word in (("l", "left"), ("r", "right")):
    for _semantic, _aliases in {
        "clavicle": {f"clavicle{_side}", f"shoulder{_side}", f"{_word}shoulder"},
        "upper_arm": {f"upperarm{_side}", f"{_word}arm", f"{_word}upperarm"},
        "forearm": {f"lowerarm{_side}", f"forearm{_side}", f"{_word}forearm"},
        "hand": {f"hand{_side}", f"{_word}hand"},
        "thigh": {f"thigh{_side}", f"{_word}upleg", f"{_word}upperleg"},
        "shin": {f"calf{_side}", f"shin{_side}", f"{_word}leg", f"{_word}lowerleg"},
        "foot": {f"foot{_side}", f"{_word}foot"},
        "toe": {f"ball{_side}", f"toe{_side}", f"toes{_side}", f"{_word}toebase"},
    }.items():
        SEMANTIC_ALIASES[f"{_word}_{_semantic}"] = _aliases


class Inspector:
    def __init__(self, glb, weight_tolerance=1e-3, nonzero_epsilon=1e-12):
        self.g, self.d = glb, glb.doc
        self.weight_tolerance, self.epsilon = weight_tolerance, nonzero_epsilon
        self.r = {
            "schema": SCHEMA, "schema_version": 1, "inspector_version": VERSION,
            "source": {"path": glb.path, "bytes": len(glb.data), "sha256": glb.sha256},
            "status": "PENDING", "structural_pass": False, "art_approved": False,
            "browser_tested": False, "android_tested": False,
            "scope": "Decoded binary structure only; no visual, contact, retarget, or runtime performance approval",
            "tolerances": {"weights_sum": weight_tolerance, "nonzero_component": nonzero_epsilon},
            "errors": [], "warnings": [], "accessors": [], "meshes": [], "skins": [],
            "nodes": [], "animations": [], "images": [], "materials": [],
            "extensions_required": self.d.get("extensionsRequired", []),
            "extensions_used": self.d.get("extensionsUsed", []),
            "container_chunks": glb.chunks,
        }

    def issue(self, severity, code, path, message, **details):
        row = {"code": code, "path": path, "message": message}
        if details:
            row["details"] = details
        self.r["errors" if severity == "error" else "warnings"].append(row)

    def error(self, code, path, message, **details):
        self.issue("error", code, path, message, **details)

    def warn(self, code, path, message, **details):
        self.issue("warning", code, path, message, **details)

    def rows(self, index, path):
        try:
            return self.g.accessor(index)
        except (GLBError, KeyError, TypeError, IndexError, struct.error) as exc:
            self.error("ACCESSOR_DECODE", path, str(exc))
            return None

    def scan_accessors(self):
        for i, a in enumerate(self.d.get("accessors", [])):
            path = f"accessors[{i}]"
            rows = self.rows(i, path)
            row = {"index": i, "type": a.get("type"), "component_type": a.get("componentType"),
                   "count": a.get("count"), "normalized": a.get("normalized", False),
                   "sparse_count": a.get("sparse", {}).get("count", 0), "implicit_zero_base": "bufferView" not in a}
            self.r["accessors"].append(row)
            if rows is None:
                row["decoded"] = False
                continue
            bad = [j for j, values in enumerate(rows) if not _finite(values)]
            row.update(decoded=True, finite=not bad, invalid_rows=bad[:8], decoded_bounds=_bounds(rows))
            if bad:
                self.error("NONFINITE_ACCESSOR", path, "Decoded data contain NaN or infinity", count=len(bad), first_rows=bad[:8])
            raw_bounds = _bounds(self.g.accessor(i, normalized=False))
            row["raw_bounds"] = raw_bounds
            for name in ("min", "max"):
                if name not in a:
                    continue
                declared, actual = a[name], raw_bounds[name]
                if not isinstance(declared, list) or actual is None or len(declared) != len(actual) or not _finite(declared):
                    self.error("ACCESSOR_BOUNDS", path, f"Invalid declared {name}")
                elif any(abs(x - y) > 1e-6 * max(1.0, abs(y)) for x, y in zip(declared, actual)):
                    self.error("ACCESSOR_BOUNDS_MISMATCH", path, f"Declared {name} differ from decoded base+sparse data", declared=declared, actual=actual)

    def scan_nodes(self):
        nodes = self.d.get("nodes", [])
        parents = {}
        for i, node in enumerate(nodes):
            path = f"nodes[{i}]"
            row = {"index": i, "name": node.get("name", ""), "mesh": node.get("mesh"), "skin": node.get("skin"), "children": node.get("children", [])}
            self.r["nodes"].append(row)
            for field, collection in (("mesh", "meshes"), ("skin", "skins")):
                if field in node:
                    try:
                        _index(self.d.get(collection, []), node[field], path + "." + field)
                    except GLBError as exc:
                        self.error("NODE_REFERENCE", path, str(exc))
            if "matrix" in node and any(k in node for k in ("translation", "rotation", "scale")):
                self.error("NODE_MATRIX_TRS", path, "Matrix and TRS cannot coexist")
            for field, size in (("matrix", 16), ("translation", 3), ("rotation", 4), ("scale", 3)):
                if field not in node:
                    continue
                value = node[field]
                if not isinstance(value, list) or len(value) != size or not _finite(value):
                    self.error("NODE_TRANSFORM", path + "." + field, "Invalid finite transform vector")
                    continue
                if field == "matrix":
                    determinant = _det3(value)
                    row["linear_determinant"] = determinant if math.isfinite(determinant) else None
                    row["singular_transform"] = abs(determinant) < 1e-12
                    if not math.isfinite(determinant):
                        self.error("TRANSFORM_OVERFLOW", path, "Finite matrix values overflow determinant evaluation")
                    if any(abs(value[j]) > 1e-6 for j in (3, 7, 11)) or abs(value[15] - 1) > 1e-6:
                        self.error("NONAFFINE_MATRIX", path, "Node matrix is not affine")
                elif field == "rotation":
                    row["quaternion_norm"] = math.hypot(*value)
                    if abs(row["quaternion_norm"] - 1) > 1e-3:
                        self.error("NODE_QUATERNION", path, "Node rotation quaternion is not normalized")
            for child in node.get("children", []):
                try:
                    _index(nodes, child, path + ".children")
                except GLBError as exc:
                    self.error("NODE_CHILD", path, str(exc)); continue
                if child in parents:
                    self.error("MULTIPLE_NODE_PARENTS", path, "A child appears more than once in the hierarchy", child=child)
                parents[child] = i
        # Iterative parent walk avoids recursion limits on valid long hierarchies.
        checked = set()
        for start in range(len(nodes)):
            current, trail = start, set()
            while current in parents and current not in checked:
                if current in trail:
                    self.error("NODE_CYCLE", f"nodes[{start}]", "Node hierarchy contains a cycle")
                    break
                trail.add(current); current = parents[current]
            checked.update(trail)

    def scan_skins(self):
        nodes = self.d.get("nodes", [])
        for i, skin in enumerate(self.d.get("skins", [])):
            path, joints = f"skins[{i}]", skin.get("joints", [])
            row = {"index": i, "name": skin.get("name", ""), "joint_count": len(joints), "joints": [],
                   "semantic_candidates": {}, "semantic_method": "name_aliases_not_anatomical_verification"}
            self.r["skins"].append(row)
            valid = []
            if not joints:
                self.error("EMPTY_SKIN", path, "Skin has no joints")
            for j in joints:
                try:
                    n = _index(nodes, j, path + ".joints")
                except GLBError as exc:
                    self.error("SKIN_JOINT", path, str(exc)); continue
                if j in valid:
                    self.error("DUPLICATE_SKIN_JOINT", path, "Skin lists a joint more than once", node=j)
                valid.append(j)
                row["joints"].append({"node": j, "name": n.get("name", "")})
            for semantic, aliases in SEMANTIC_ALIASES.items():
                found = [j for j in row["joints"] if _bone_key(j["name"]) in aliases]
                if found:
                    row["semantic_candidates"][semantic] = found
            row["unmapped_semantics"] = [k for k in SEMANTIC_ALIASES if k not in row["semantic_candidates"]]
            row["ambiguous_semantics"] = [k for k, v in row["semantic_candidates"].items() if len(v) > 1]
            if "skeleton" in skin:
                try:
                    _index(nodes, skin["skeleton"], path + ".skeleton")
                except GLBError as exc:
                    self.error("SKIN_SKELETON", path, str(exc))
            if "inverseBindMatrices" in skin:
                matrices = self.rows(skin["inverseBindMatrices"], path + ".inverseBindMatrices")
                a = _index(self.d.get("accessors", []), skin["inverseBindMatrices"], path)
                if a.get("type") != "MAT4" or a.get("componentType") != 5126 or (matrices is not None and len(matrices) < len(joints)):
                    self.error("INVERSE_BIND_LAYOUT", path, "Inverse bind matrices must be FLOAT MAT4 and cover every joint")
                if matrices is not None and all(len(m) == 16 and _finite(m) for m in matrices):
                    determinants = [_det3(m) for m in matrices]
                    row["inverse_bind"] = {"count": len(matrices), "determinant_min": min(determinants), "determinant_max": max(determinants),
                                           "singular_count": sum(abs(d) < 1e-12 for d in determinants)}
                    if row["inverse_bind"]["singular_count"]:
                        self.warn("SINGULAR_INVERSE_BIND", path, "Inverse bind matrix contains a singular linear transform")
            else:
                row["inverse_bind"] = {"implicit_identity": True, "count": len(joints)}

    def scan_meshes(self):
        nodes, accessors = self.d.get("nodes", []), self.d.get("accessors", [])
        for mi, mesh in enumerate(self.d.get("meshes", [])):
            target_names = mesh.get("extras", {}).get("targetNames", []) if isinstance(mesh.get("extras", {}), dict) else []
            mr = {"index": mi, "name": mesh.get("name", ""), "primitives": []}
            self.r["meshes"].append(mr)
            target_counts = {len(p.get("targets", [])) for p in mesh.get("primitives", [])}
            if len(target_counts) > 1:
                self.error("MESH_MORPH_COUNTS", f"meshes[{mi}]", "All primitives in one mesh must have the same morph target count")
            for pi, primitive in enumerate(mesh.get("primitives", [])):
                path = f"meshes[{mi}].primitives[{pi}]"
                attrs = primitive.get("attributes", {})
                decoded = {k: self.rows(v, path + ".attributes." + k) for k, v in attrs.items()}
                position = decoded.get("POSITION")
                pr = {"index": pi, "mode": primitive.get("mode", 4), "material": primitive.get("material"), "attributes": attrs,
                      "vertex_count": len(position) if position is not None else None, "morph_targets": []}
                mr["primitives"].append(pr)
                if position is None:
                    self.error("POSITION_MISSING", path, "No decoded POSITION data; compressed-only primitives are unsupported")
                    continue
                count = len(position)
                if any(len(v) != 3 for v in position):
                    self.error("POSITION_LAYOUT", path, "POSITION must be VEC3")
                pr["position_bounds_local"] = _bounds(position)
                for semantic, rows in decoded.items():
                    if rows is not None and len(rows) != count:
                        self.error("ATTRIBUTE_COUNT", path + "." + semantic, "Vertex attribute count differs from POSITION")
                normal = decoded.get("NORMAL")
                if normal is not None:
                    lengths = [math.sqrt(sum(v * v for v in row)) for row in normal if len(row) == 3 and _finite(row)]
                    if len(lengths) != count:
                        self.error("NORMAL_LAYOUT", path, "NORMAL must be a finite VEC3 per vertex")
                    if lengths:
                        pr["normals"] = {"length_min": min(lengths), "length_max": max(lengths), "zero_count": sum(n < 1e-12 for n in lengths),
                                         "max_unit_error": max(abs(n - 1) for n in lengths)}
                        if pr["normals"]["zero_count"]:
                            self.error("ZERO_NORMAL", path, "Base normals contain zero-length vectors", count=pr["normals"]["zero_count"])
                        elif pr["normals"]["max_unit_error"] > .02:
                            self.warn("NONUNIT_NORMAL", path, "Normals deviate from unit length; check quantization and renderer renormalization", **pr["normals"])
                else:
                    self.warn("NORMAL_ABSENT", path, "Base normals are absent; renderer-generated normals were not evaluated")
                if "indices" in primitive:
                    indices_rows = self.rows(primitive["indices"], path + ".indices")
                    a = _index(accessors, primitive["indices"], path + ".indices")
                    if a.get("type") != "SCALAR" or a.get("componentType") not in (5121, 5123, 5125) or a.get("normalized"):
                        self.error("INDEX_LAYOUT", path, "Indices must be unnormalized unsigned SCALAR")
                    indices = [r[0] for r in indices_rows] if indices_rows else []
                    bad = [j for j, v in enumerate(indices) if not isinstance(v, int) or not 0 <= v < count]
                    if bad:
                        self.error("INDEX_BOUNDS", path, "Decoded indices exceed POSITION bounds", count=len(bad), first_indices=bad[:8])
                else:
                    indices = range(count)
                n = len(indices)
                mode = pr["mode"]
                pr["index_count"] = n
                if mode not in range(7):
                    self.error("PRIMITIVE_MODE", path, "Unsupported primitive mode")
                if mode == 4 and n % 3:
                    self.error("TRIANGLE_INDEX_COUNT", path, "TRIANGLES index count is not divisible by three")
                if mode == 1 and n % 2:
                    self.error("LINE_INDEX_COUNT", path, "LINES index count is not divisible by two")
                pr["triangle_count"] = n // 3 if mode == 4 else max(0, n - 2) if mode in (5, 6) else 0
                self.scan_weights(mi, path, attrs, decoded, count, pr)
                targets = primitive.get("targets", [])
                if target_names and len(target_names) != len(targets):
                    self.error("MORPH_NAME_COUNT", path, "targetNames count differs from target count")
                for ti, target in enumerate(targets):
                    tr = {"index": ti, "name": target_names[ti] if ti < len(target_names) else f"target_{ti}", "attributes": {}}
                    pr["morph_targets"].append(tr)
                    for semantic, ai in target.items():
                        rows = self.rows(ai, path + f".targets[{ti}].{semantic}")
                        if rows is None:
                            continue
                        if len(rows) != count or any(len(r) != 3 for r in rows):
                            self.error("MORPH_LAYOUT", path, "Morph deltas must be VEC3 and match POSITION count", target=ti, semantic=semantic)
                        valid = [r for r in rows if _finite(r)]
                        lengths = [math.sqrt(sum(v * v for v in r)) for r in valid]
                        nz = sum(any(abs(v) > self.epsilon for v in r) for r in valid)
                        tr["attributes"][semantic] = {"accessor": ai, "decoded_vertices": len(rows), "finite": len(valid) == len(rows),
                            "nonzero_vertices": nz, "exact_nonzero_vertices": sum(any(v != 0 for v in r) for r in valid),
                            "maximum_delta_length": max(lengths, default=0.0), "bounds": _bounds(rows)}
                    tr["has_nonzero_position"] = tr["attributes"].get("POSITION", {}).get("nonzero_vertices", 0) > 0
                    if not any(v["nonzero_vertices"] for v in tr["attributes"].values()):
                        self.warn("ZERO_MORPH", path + f".targets[{ti}]", "Actual decoded morph is zero; a name or declared max is not evidence of movement", name=tr["name"])
                if targets and not any("NORMAL" in t for t in targets):
                    self.warn("MORPH_NORMALS_ABSENT", path, "Morph normal deltas are absent; expression shading requires actual renderer review")

    def scan_weights(self, mesh_index, path, attrs, decoded, count, pr):
        joints = {k[7:]: k for k in attrs if k.startswith("JOINTS_")}
        weights = {k[8:]: k for k in attrs if k.startswith("WEIGHTS_")}
        if not joints and not weights:
            return
        if set(joints) != set(weights):
            self.error("SKIN_ATTRIBUTE_PAIRS", path, "JOINTS_n and WEIGHTS_n sets do not match")
        pairs = sorted(set(joints) & set(weights))
        arrays = []
        for suffix in pairs:
            ji, wi = attrs[joints[suffix]], attrs[weights[suffix]]
            ja, wa = _index(self.d["accessors"], ji, path), _index(self.d["accessors"], wi, path)
            jr, wr = decoded[joints[suffix]], decoded[weights[suffix]]
            if ja.get("type") != "VEC4" or ja.get("componentType") not in (5121, 5123) or ja.get("normalized"):
                self.error("JOINTS_LAYOUT", path, "JOINTS must be unnormalized unsigned byte/short VEC4")
            if wa.get("type") != "VEC4" or wa.get("componentType") not in (5121, 5123, 5126) or (wa.get("componentType") != 5126 and not wa.get("normalized")):
                self.error("WEIGHTS_LAYOUT", path, "WEIGHTS must be FLOAT or normalized unsigned byte/short VEC4")
            if jr is not None and wr is not None and len(jr) == count and len(wr) == count:
                arrays.append((jr, wr))
        if not arrays:
            return
        sums, active, negative, outside = [], [], 0, 0
        for i in range(count):
            row = [v for _, wr in arrays for v in wr[i]]
            if not _finite(row):
                continue
            sums.append(sum(row)); active.append(sum(v > self.epsilon for v in row))
            negative += sum(v < 0 for v in row)
            outside += sum(v > 1 + self.weight_tolerance for v in row)
        bad = sum(abs(v - 1) > self.weight_tolerance for v in sums)
        pr["weights"] = {"sets": pairs, "vertices_measured": len(sums), "sum_min": min(sums, default=None), "sum_max": max(sums, default=None),
                         "max_sum_error": max((abs(v - 1) for v in sums), default=None), "non_normalized_vertices": bad,
                         "negative_components": negative, "components_above_one": outside, "maximum_active_influences": max(active, default=0)}
        if bad or negative or outside:
            self.error("WEIGHTS_NOT_NORMALIZED", path, "Decoded weights violate nonnegative normalized skinning", **pr["weights"])
        bindings = [(i, n) for i, n in enumerate(self.d.get("nodes", [])) if n.get("mesh") == mesh_index and "skin" in n]
        if not bindings:
            self.warn("UNBOUND_SKIN_ATTRIBUTES", path, "Skin attributes exist without a skinned node instance")
        for ni, node in bindings:
            try:
                skin = _index(self.d.get("skins", []), node["skin"], path + ".skin")
            except GLBError as exc:
                self.error("SKIN_REFERENCE", path, str(exc)); continue
            joint_count = len(skin.get("joints", []))
            invalid = sum(not isinstance(v, int) or not 0 <= v < joint_count for jr, _ in arrays for row in jr for v in row)
            if invalid:
                self.error("JOINT_INDEX_BOUNDS", path, "JOINTS values are indices into the bound skin, and some are out of range", node=ni, joint_count=joint_count, invalid_components=invalid)

    def scan_animations(self):
        nodes = self.d.get("nodes", [])
        for ai, animation in enumerate(self.d.get("animations", [])):
            path = f"animations[{ai}]"
            ar = {"index": ai, "name": animation.get("name", f"animation_{ai}"), "channels": [], "changing_channels": 0}
            self.r["animations"].append(ar)
            seen, starts, ends = set(), [], []
            for ci, channel in enumerate(animation.get("channels", [])):
                cp, target = path + f".channels[{ci}]", channel.get("target", {})
                try:
                    sampler = _index(animation.get("samplers", []), channel.get("sampler"), cp + ".sampler")
                    node = _index(nodes, target.get("node"), cp + ".target.node")
                    ia = _index(self.d.get("accessors", []), sampler.get("input"), cp + ".input")
                    oa = _index(self.d.get("accessors", []), sampler.get("output"), cp + ".output")
                except GLBError as exc:
                    self.error("ANIMATION_REFERENCE", cp, str(exc)); continue
                prop, interpolation = target.get("path"), sampler.get("interpolation", "LINEAR")
                identity = (target["node"], prop)
                if identity in seen:
                    self.error("DUPLICATE_ANIMATION_TARGET", cp, "Node/property targeted more than once in one clip")
                seen.add(identity)
                times_rows, values = self.rows(sampler["input"], cp + ".input"), self.rows(sampler["output"], cp + ".output")
                if times_rows is None or values is None:
                    continue
                if ia.get("type") != "SCALAR" or ia.get("componentType") != 5126:
                    self.error("ANIMATION_TIME_LAYOUT", cp, "Time accessor must be FLOAT SCALAR")
                times = [r[0] for r in times_rows]
                valid_times = _finite(times) and times[0] >= 0 and all(b > a for a, b in zip(times, times[1:]))
                if not valid_times:
                    self.error("ANIMATION_TIME_ORDER", cp, "Times must be finite, nonnegative and strictly increasing")
                if "min" not in ia or "max" not in ia:
                    self.warn("ANIMATION_TIME_BOUNDS_ABSENT", cp, "Input accessor lacks required min/max metadata")
                width = 1
                if prop == "weights":
                    try:
                        mesh = _index(self.d.get("meshes", []), node.get("mesh"), cp + ".mesh")
                        widths = {len(p.get("targets", [])) for p in mesh.get("primitives", [])}
                        if len(widths) != 1 or not next(iter(widths)):
                            raise GLBError("Weight animation requires a consistent nonzero target count")
                        width = next(iter(widths))
                    except GLBError as exc:
                        self.error("MORPH_ANIMATION_TARGET", cp, str(exc)); continue
                expected_type = {"translation": "VEC3", "rotation": "VEC4", "scale": "VEC3", "weights": "SCALAR"}.get(prop)
                if expected_type is None or oa.get("type") != expected_type:
                    self.error("ANIMATION_OUTPUT_LAYOUT", cp, "Output accessor type does not match animated property")
                if interpolation not in ("LINEAR", "STEP", "CUBICSPLINE"):
                    self.error("ANIMATION_INTERPOLATION", cp, "Unsupported interpolation mode")
                factor = 3 if interpolation == "CUBICSPLINE" else 1
                if factor == 3 and len(times) < 2:
                    self.error("CUBIC_KEY_COUNT", cp, "CUBICSPLINE requires at least two keys")
                expected = len(times) * factor * width
                cr = {"index": ci, "node": target["node"], "node_name": node.get("name", ""), "path": prop,
                      "interpolation": interpolation, "input_samples": len(times), "output_elements": len(values),
                      "expected_output_elements": expected, "morph_target_count": width if prop == "weights" else None}
                ar["channels"].append(cr)
                if len(values) != expected:
                    self.error("ANIMATION_OUTPUT_COUNT", cp, "Output count does not match time/target/interpolation layout", expected=expected, actual=len(values))
                    continue
                sample_values = []
                for k in range(len(times)):
                    start = k * factor * width + (width if factor == 3 else 0)
                    sample_values.append(tuple(v for row in values[start:start + width] for v in row))
                if not all(_finite(v) for v in sample_values):
                    self.error("ANIMATION_NONFINITE", cp, "Animation values contain NaN/infinity")
                    continue
                change = max((max(abs(a - b) for a, b in zip(sample_values[0], v)) for v in sample_values), default=0)
                cr["max_key_delta_from_first"] = change
                cr["changing"] = change > self.epsilon
                ar["changing_channels"] += int(cr["changing"])
                if prop == "rotation":
                    err = max(abs(math.sqrt(sum(x * x for x in v)) - 1) for v in sample_values)
                    cr["max_quaternion_norm_error"] = err
                    if err > .01:
                        self.error("ANIMATION_QUATERNION", cp, "Rotation key values are not normalized", max_error=err)
                if valid_times:
                    starts.append(times[0]); ends.append(times[-1])
            ar["time_start_s"] = min(starts) if starts else None
            ar["time_end_s"] = max(ends) if ends else None
            ar["sampled_span_s"] = max(ends) - min(starts) if starts else None
            ar["duration_from_zero_s"] = max(ends) if ends else None

    def scan_images_materials(self):
        for i, info in enumerate(self.d.get("images", [])):
            row = {"index": i, "name": info.get("name", ""), "declared_mime_type": info.get("mimeType")}
            self.r["images"].append(row)
            try:
                data = self.g.image_bytes(i)
                row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
                row.update(image_dimensions(data))
                mime = {"PNG": "image/png", "JPEG": "image/jpeg"}[row["format"]]
                if info.get("mimeType") and info["mimeType"] != mime:
                    self.error("IMAGE_MIME_MISMATCH", f"images[{i}]", "Image signature differs from declared mimeType")
            except GLBError as exc:
                self.error("IMAGE_UNVERIFIED", f"images[{i}]", str(exc))
        textures = self.d.get("textures", [])
        for i, material in enumerate(self.d.get("materials", [])):
            pbr = material.get("pbrMetallicRoughness", {})
            row = {"index": i, "name": material.get("name", ""), "alpha_mode": material.get("alphaMode", "OPAQUE"),
                   "double_sided": material.get("doubleSided", False), "normal_texture": material.get("normalTexture"),
                   "base_color_texture": pbr.get("baseColorTexture"), "metallic_factor": pbr.get("metallicFactor", 1),
                   "roughness_factor": pbr.get("roughnessFactor", 1)}
            self.r["materials"].append(row)
            for entry in (material.get("normalTexture"), material.get("occlusionTexture"), material.get("emissiveTexture"),
                          pbr.get("baseColorTexture"), pbr.get("metallicRoughnessTexture")):
                if entry is None:
                    continue
                try:
                    texture = _index(textures, entry.get("index"), f"materials[{i}].texture")
                    if "source" in texture:
                        _index(self.d.get("images", []), texture["source"], f"materials[{i}].texture.source")
                    else:
                        raise GLBError("Texture source uses an unsupported extension or is absent")
                except GLBError as exc:
                    self.error("TEXTURE_REFERENCE", f"materials[{i}]", str(exc))

    def run(self):
        for name in ("KHR_draco_mesh_compression", "EXT_meshopt_compression"):
            if name in self.d.get("extensionsRequired", []):
                self.error("UNSUPPORTED_COMPRESSION", "extensionsRequired", "Required compressed geometry is not decoded by this inspector", extension=name)
            elif name in self.d.get("extensionsUsed", []):
                self.warn("COMPRESSION_FALLBACK_ONLY", "extensionsUsed", "Only uncompressed core fallback data are inspected", extension=name)
        for method in (self.scan_accessors, self.scan_nodes, self.scan_skins, self.scan_meshes, self.scan_animations, self.scan_images_materials):
            try:
                method()
            except (GLBError, KeyError, TypeError, IndexError, ValueError, OverflowError) as exc:
                self.error("MALFORMED_STRUCTURE", method.__name__, str(exc))
        primitives = [p for m in self.r["meshes"] for p in m["primitives"]]
        targets = [t for p in primitives for t in p["morph_targets"]]
        self.r["summary"] = {
            "mesh_count": len(self.r["meshes"]), "primitive_count": len(primitives),
            "position_vertices_per_primitive_sum": sum(p.get("vertex_count") or 0 for p in primitives),
            "triangle_count": sum(p.get("triangle_count", 0) for p in primitives),
            "skin_count": len(self.r["skins"]), "joint_counts": [s["joint_count"] for s in self.r["skins"]],
            "morph_target_instances": len(targets), "nonzero_position_target_instances": sum(t.get("has_nonzero_position", False) for t in targets),
            "animation_count": len(self.r["animations"]), "animation_names": [a["name"] for a in self.r["animations"]],
            "image_count": len(self.r["images"]), "error_count": len(self.r["errors"]), "warning_count": len(self.r["warnings"]),
        }
        self.r["structural_pass"] = not self.r["errors"]
        self.r["status"] = "STRUCTURE_PASS" if self.r["structural_pass"] else "STRUCTURE_FAIL"
        return self.r


def _failure(source, exc, data=None):
    return {"schema": SCHEMA, "schema_version": 1, "inspector_version": VERSION,
            "source": {"path": str(source), "bytes": len(data) if data is not None else None,
                       "sha256": hashlib.sha256(data).hexdigest() if data is not None else None},
            "status": "STRUCTURE_FAIL", "structural_pass": False, "art_approved": False,
            "browser_tested": False, "android_tested": False,
            "scope": "Decoded binary structure only; no visual, contact, retarget, or runtime performance approval",
            "tolerances": {"weights_sum": 1e-3, "nonzero_component": 1e-12},
            "errors": [{"code": "CONTAINER_OR_IO", "path": "container", "message": str(exc)}], "warnings": [],
            "accessors": [], "meshes": [], "skins": [], "nodes": [], "animations": [], "images": [], "materials": [],
            "extensions_required": [], "extensions_used": [], "container_chunks": [],
            "summary": {"mesh_count": 0, "primitive_count": 0, "position_vertices_per_primitive_sum": 0,
                        "triangle_count": 0, "skin_count": 0, "joint_counts": [], "morph_target_instances": 0,
                        "nonzero_position_target_instances": 0, "animation_count": 0, "animation_names": [],
                        "image_count": 0, "error_count": 1, "warning_count": 0}}


def inspect_bytes(data, label="<memory>", weight_tolerance=1e-3, nonzero_epsilon=1e-12):
    try:
        return Inspector(GLB(data, label), weight_tolerance, nonzero_epsilon).run()
    except (GLBError, OSError, ValueError, TypeError, KeyError, IndexError, struct.error) as exc:
        return _failure(label, exc, data)


def inspect_glb(path, weight_tolerance=1e-3, nonzero_epsilon=1e-12):
    try:
        data = Path(path).read_bytes()
    except OSError as exc:
        return _failure(path, exc)
    return inspect_bytes(data, str(path), weight_tolerance, nonzero_epsilon)


def _fixture(doc, binary):
    """In-memory fixture only; never writes test assets into the workspace."""
    doc = dict(doc)
    doc["asset"] = {"version": "2.0"}
    doc["buffers"] = [{"byteLength": len(binary)}]
    j = json.dumps(doc, separators=(",", ":")).encode()
    j += b" " * (-len(j) % 4)
    b = bytes(binary) + b"\0" * (-len(binary) % 4)
    return struct.pack("<4sII", b"glTF", 2, 28 + len(j) + len(b)) + struct.pack("<I4s", len(j), b"JSON") + j + struct.pack("<I4s", len(b), b"BIN\0") + b


def self_test():
    """Focused regressions: stride, sparse, implicit zero, normalization, padding."""
    passed = []
    # NaN padding must never be interpreted as a fourth POSITION component.
    binary = struct.pack("<8f", 1, 2, 3, math.nan, 7, 8, 9, math.nan) + b"\x01\0\0\0" + struct.pack("<3f", 4, 5, 6)
    doc = {"bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 32, "byteStride": 16},
                           {"buffer": 0, "byteOffset": 32, "byteLength": 1}, {"buffer": 0, "byteOffset": 36, "byteLength": 12}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 2, "type": "VEC3",
                          "sparse": {"count": 1, "indices": {"bufferView": 1, "componentType": 5121}, "values": {"bufferView": 2}}}]}
    g = GLB(_fixture(doc, binary))
    assert g.accessor(0) == [(1., 2., 3.), (4., 5., 6.)]
    assert inspect_bytes(g.data)["structural_pass"]
    passed.append("interleaved_stride_and_sparse_replacement_ignore_padding")
    implicit = json.loads(json.dumps(doc))
    implicit["accessors"][0].pop("bufferView")
    implicit["accessors"][0]["count"] = 3
    assert GLB(_fixture(implicit, binary)).accessor(0) == [(0, 0, 0), (4., 5., 6.), (0, 0, 0)]
    passed.append("implicit_zero_sparse_is_actual_nonzero")
    forged = json.loads(json.dumps(implicit))
    forged["accessors"][0]["max"] = [0, 0, 0]
    report = inspect_bytes(_fixture(forged, binary))
    assert not report["structural_pass"] and any(e["code"] == "ACCESSOR_BOUNDS_MISMATCH" for e in report["errors"])
    passed.append("metadata_cannot_hide_actual_sparse_values")
    ndoc = {"bufferViews": [{"buffer": 0, "byteLength": 3}, {"buffer": 0, "byteOffset": 4, "byteLength": 4}],
            "accessors": [{"bufferView": 0, "componentType": 5120, "count": 1, "type": "VEC3", "normalized": True},
                          {"bufferView": 1, "componentType": 5123, "count": 1, "type": "VEC2", "normalized": True}]}
    ng = GLB(_fixture(ndoc, struct.pack("<3bB2H", -128, 0, 127, 0, 0, 65535)))
    assert ng.accessor(0) == [(-1., 0., 1.)] and ng.accessor(1) == [(0., 1.)]
    assert ng.accessor(0, normalized=False) == [(-128, 0, 127)]
    passed.append("signed_and_unsigned_normalization_preserve_raw_values")
    mdoc = {"bufferViews": [{"buffer": 0, "byteLength": 11}],
            "accessors": [{"bufferView": 0, "componentType": 5121, "count": 1, "type": "MAT3"}]}
    assert GLB(_fixture(mdoc, bytes([1, 2, 3, 99, 4, 5, 6, 99, 7, 8, 9]))).accessor(0) == [tuple(range(1, 10))]
    passed.append("matrix_column_padding_with_optional_final_padding")
    bad_binary = binary[:32] + b"\x03\0\0\0" + binary[36:]
    try:
        GLB(_fixture(doc, bad_binary)).accessor(0)
    except GLBError:
        pass
    else:
        raise AssertionError("Out-of-range sparse index was accepted")
    duplicates = json.loads(json.dumps(doc))
    duplicates["accessors"][0]["sparse"]["count"] = 2
    duplicates["bufferViews"][1]["byteLength"] = 2
    duplicates["bufferViews"][2]["byteLength"] = 24
    duplicate_binary = binary[:32] + b"\x01\x01\0\0" + struct.pack("<6f", 4, 5, 6, 7, 8, 9)
    try:
        GLB(_fixture(duplicates, duplicate_binary)).accessor(0)
    except GLBError:
        pass
    else:
        raise AssertionError("Duplicate sparse indices were accepted")
    short = json.loads(json.dumps(doc)); short["bufferViews"][0]["byteLength"] = 20
    try:
        GLB(_fixture(short, binary)).accessor(0)
    except GLBError:
        pass
    else:
        raise AssertionError("Out-of-bounds stride was accepted")
    passed.append("sparse_and_stride_bounds_fail_closed")
    return {"status": "SELF_TEST_PASS", "tests": passed, "count": len(passed), "scope": "Binary decoder regressions; no art or device validation"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("glb", nargs="?", type=Path)
    parser.add_argument("--out", type=Path, help="Write the full JSON report; input is never overwritten")
    parser.add_argument("--self-test", action="store_true", help="Run focused in-memory regression fixtures")
    args = parser.parse_args(argv)
    if args.self_test:
        result = self_test()
        print(json.dumps(result, indent=2))
        return 0
    if args.glb is None:
        parser.error("Supply path.glb or --self-test")
    report = inspect_glb(args.glb)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if args.out:
        if args.out.resolve() == args.glb.resolve():
            parser.error("--out must not overwrite the input GLB")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
        print(json.dumps({"status": report["status"], "summary": report["summary"], "report": str(args.out), "art_approved": False}, ensure_ascii=False))
    else:
        print(payload, end="")
    return 0 if report["structural_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
