"""Patch spriteatlas.ab for custom item icons (OGODJ bundle format)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import UnityPy
from PIL import Image

from game_data import patch_unity_version_parser
from patch_common import GAME_ROOT

HEADER = b"OGODJ\x01\x00\x00"
ASSETS_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets" / "Assets"
STREAMING_DIR = GAME_ROOT / "AnimOdyssey_Data" / "StreamingAssets"
SPRITEATLAS_AB = ASSETS_DIR / "spriteatlas.ab"
SPRITEATLAS_BACKUP = ASSETS_DIR / "spriteatlas.ab.ignite_mod.bak"
ASSET_MAP = STREAMING_DIR / "asset_map.json"
ASSET_MAP_BACKUP = ASSET_MAP.with_suffix(".json.ignite_mod.bak")

ICON_SPRITE_NAME = "Red_weapon_004"
ICON_ATLAS_NAME = "ItemIcon"
ICON_SIZE = (195, 195)


def _backup_is_stale() -> bool:
    if not SPRITEATLAS_BACKUP.exists() or not SPRITEATLAS_AB.exists():
        return False
    live_size = SPRITEATLAS_AB.stat().st_size
    backup_size = SPRITEATLAS_BACKUP.stat().st_size
    return live_size > backup_size * 2 or backup_size > live_size * 2


def ensure_spriteatlas_backup() -> None:
    if not SPRITEATLAS_AB.exists():
        raise SystemExit(f"找不到 {SPRITEATLAS_AB}")
    if SPRITEATLAS_BACKUP.exists() and _backup_is_stale():
        SPRITEATLAS_BACKUP.unlink()
        print(
            "  [warn] 偵測到遊戲已更新（spriteatlas.ab 與備份大小不符），"
            "已刪除舊備份並從目前遊戲檔重建"
        )
    if not SPRITEATLAS_BACKUP.exists():
        shutil.copy2(SPRITEATLAS_AB, SPRITEATLAS_BACKUP)
        print(f"  [backup] {SPRITEATLAS_BACKUP.name}")


def restore_spriteatlas_from_backup() -> None:
    if not SPRITEATLAS_BACKUP.exists():
        return
    if SPRITEATLAS_AB.exists() and _backup_is_stale():
        print(
            "  [skip] spriteatlas 備份與現行檔大小差異過大，跳過還原（避免用舊版覆蓋遊戲更新後的資源）"
        )
        shutil.copy2(SPRITEATLAS_AB, SPRITEATLAS_BACKUP)
        print(f"  [backup] 已從現行檔重建 {SPRITEATLAS_BACKUP.name}")
        return
    shutil.copy2(SPRITEATLAS_BACKUP, SPRITEATLAS_AB)
    if ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP_BACKUP, ASSET_MAP)


def apply_sprite_replacement(sprite_name: str, image_path: Path) -> None:
    ensure_spriteatlas_backup()
    patch_unity_version_parser()

    source = _fit_icon(Image.open(image_path).convert("RGBA"), ICON_SIZE)

    # 一律以「目前遊戲內」spriteatlas 為基底（備份可能來自舊版遊戲）
    base_ab = SPRITEATLAS_AB if SPRITEATLAS_AB.exists() else SPRITEATLAS_BACKUP
    payload = base_ab.read_bytes()[len(HEADER) :]
    env = UnityPy.load(payload)

    atlas_obj = None
    for obj in env.objects:
        if obj.type.name == "SpriteAtlas" and obj.read().m_Name == ICON_ATLAS_NAME:
            atlas_obj = obj
            break
    if atlas_obj is None:
        raise SystemExit(f"spriteatlas.ab 找不到 SpriteAtlas：{ICON_ATLAS_NAME}")

    atlas_tree = atlas_obj.read_typetree()
    names = atlas_tree.get("m_PackedSpriteNamesToIndex", [])
    if sprite_name not in names:
        raise SystemExit(f"ItemIcon 圖集找不到 Sprite：{sprite_name}")

    idx = names.index(sprite_name)
    render_entry = atlas_tree["m_RenderDataMap"][idx][1]
    texture_ref = render_entry["texture"]
    rect = render_entry["textureRect"]
    path_id = texture_ref["m_PathID"]

    tex_obj = next((o for o in env.objects if o.path_id == path_id), None)
    if tex_obj is None:
        raise SystemExit(f"找不到 ItemIcon 紋理 path_id={path_id}")

    tex = tex_obj.read()
    atlas_image = tex.image.copy()
    x = int(rect["x"])
    y = int(rect["y"])
    w = int(rect["width"])
    h = int(rect["height"])
    icon = source.resize((w, h), Image.Resampling.LANCZOS)
    atlas_image.paste(icon, (x, y), icon)
    tex.image = atlas_image
    tex_obj.patch(tex)

    saved = next(iter(env.files.values())).save()
    SPRITEATLAS_AB.write_bytes(HEADER + saved)
    _update_asset_map_size(len(saved))
    print(
        f"  [ok]   spriteatlas {sprite_name} → ItemIcon 紋理 ({w}×{h} @ {x},{y})"
    )


def _fit_icon(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    image.thumbnail(size, Image.Resampling.LANCZOS)
    offset = ((size[0] - image.width) // 2, (size[1] - image.height) // 2)
    canvas.paste(image, offset, image)
    return canvas


def _update_asset_map_size(bundle_size_without_prefix: int) -> None:
    if not ASSET_MAP_BACKUP.exists():
        shutil.copy2(ASSET_MAP, ASSET_MAP_BACKUP)

    asset_map = json.loads(ASSET_MAP.read_text(encoding="utf-8"))
    if "size" in asset_map and "spriteatlas.ab" in asset_map["size"]:
        asset_map["size"]["spriteatlas.ab"] = bundle_size_without_prefix
    ASSET_MAP.write_text(
        json.dumps(asset_map, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
