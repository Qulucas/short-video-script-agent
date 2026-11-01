from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple, Union

from src.schemas import DRAFT_KEYS

PATH_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")
DRAFT_PATCH_KEYS = ("title",) + DRAFT_KEYS


def parse_path(path: str) -> List[Union[str, int]]:
    """"dialogue[0].line" -> ["dialogue", 0, "line"]; raises ValueError on anything else."""
    parts: List[Union[str, int]] = []
    pos = 0
    text = str(path)
    while pos < len(text):
        if text[pos] == "." and parts:
            pos += 1
        m = PATH_RE.match(text, pos)
        if not m:
            raise ValueError("无法解析路径 %r" % path)
        parts.append(m.group(1) if m.group(1) is not None else int(m.group(2)))
        pos = m.end()
    if not parts or not isinstance(parts[0], str):
        raise ValueError("路径必须以字段名开头：%r" % path)
    return parts


def _walk(node: Any, parts: List[Union[str, int]], create: bool) -> Tuple[Any, Union[str, int]]:
    for i, part in enumerate(parts[:-1]):
        nxt = parts[i + 1]
        if isinstance(part, int):
            if not isinstance(node, list) or part >= len(node):
                raise ValueError("下标 %d 超出范围" % part)
            node = node[part]
            continue
        if not isinstance(node, dict):
            raise ValueError("%s 不是对象" % part)
        if part not in node:
            if not create:
                raise ValueError("字段 %s 不存在" % part)
            node[part] = [] if isinstance(nxt, int) else {}
        node = node[part]
    return node, parts[-1]


def _set(target: Dict[str, Any], path: str, value: Any) -> None:
    parts = parse_path(path)
    node, last = _walk(target, parts, create=True)
    if isinstance(last, int):
        if not isinstance(node, list) or last > len(node):
            raise ValueError("下标 %d 超出范围（追加请用当前长度 %d）" % (last, len(node) if isinstance(node, list) else 0))
        if last == len(node):
            node.append(copy.deepcopy(value))
        else:
            node[last] = copy.deepcopy(value)
    else:
        if not isinstance(node, dict):
            raise ValueError("%s 的上一级不是对象" % last)
        node[last] = copy.deepcopy(value)


def _unset(target: Dict[str, Any], path: str) -> None:
    parts = parse_path(path)
    node, last = _walk(target, parts, create=False)
    if isinstance(last, int):
        if not isinstance(node, list) or last >= len(node):
            raise ValueError("下标 %d 超出范围" % last)
        node.pop(last)
    elif isinstance(node, dict) and last in node:
        node.pop(last)
    else:
        raise ValueError("字段 %s 不存在" % last)


def apply_patches(draft: Dict[str, Any], patches: Any) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """Apply local edits to a copy of the draft. Returns (new_draft, errors, touched).

    Ops: {"shot": id, "set": {path: value}, "unset": [path]} edits one shot;
    {"draft": true, "set"/"unset"} edits top-level keys (title, audio_tracks, fulfills, waivers,
    deviations; not shots); {"insert_shot": {...}, "after": id} and {"remove_shot": id}.
    Nothing is applied when any op fails, so a bad patch never leaves a half-edited draft.
    """
    out = copy.deepcopy(draft)
    errors: List[str] = []
    touched: List[str] = []
    if not isinstance(patches, list) or not patches:
        return draft, ["patches 必须是非空数组"], []
    for i, op in enumerate(patches):
        label = "patches[%d]" % i
        if not isinstance(op, dict):
            errors.append(label + " 必须是对象")
            continue
        shots = out.get("shots") or []
        ids = [s.get("id") for s in shots]
        try:
            if "remove_shot" in op:
                sid = op["remove_shot"]
                if sid not in ids:
                    raise ValueError("没有分镜 %s" % sid)
                out["shots"] = [s for s in shots if s.get("id") != sid]
                touched.append(str(sid))
            elif "insert_shot" in op:
                shot = op["insert_shot"]
                if not isinstance(shot, dict) or not shot.get("id"):
                    raise ValueError("insert_shot 需要带 id 的分镜对象")
                if shot["id"] in ids:
                    raise ValueError("分镜 id %s 已存在" % shot["id"])
                after = op.get("after")
                if after is not None and after not in ids:
                    raise ValueError("after 指向不存在的分镜 %s" % after)
                at = ids.index(after) + 1 if after is not None else 0
                out["shots"] = shots[:at] + [copy.deepcopy(shot)] + shots[at:]
                touched.append(str(shot["id"]))
            elif op.get("draft") is True:
                for path in list((op.get("set") or {})) + list(op.get("unset") or []):
                    if parse_path(path)[0] not in DRAFT_PATCH_KEYS:
                        raise ValueError("草稿级补丁只能改 %s；分镜请用 shot 操作" % "/".join(DRAFT_PATCH_KEYS))
                for path, value in (op.get("set") or {}).items():
                    _set(out, path, value)
                for path in op.get("unset") or []:
                    _unset(out, path)
                touched.append("draft")
            elif "shot" in op:
                sid = op["shot"]
                if sid not in ids:
                    raise ValueError("没有分镜 %s" % sid)
                shot = shots[ids.index(sid)]
                for path, value in (op.get("set") or {}).items():
                    if parse_path(path)[0] == "id":
                        raise ValueError("不能改分镜 id")
                    _set(shot, path, value)
                for path in op.get("unset") or []:
                    _unset(shot, path)
                touched.append(str(sid))
            else:
                raise ValueError("需要 shot / draft / insert_shot / remove_shot 之一")
        except ValueError as exc:
            errors.append("%s：%s" % (label, exc))
    if errors:
        return draft, errors, []
    return out, [], list(dict.fromkeys(touched))
