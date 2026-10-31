from __future__ import annotations

import copy
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import DATA_DIR, load_json
from src.render import exit_code_for
from src.schemas import draft_hash, normalize_brief, parse_action, validate_draft
from src.tools.citations import check_citations
from src.tools.duration import estimate_draft
from src.tools.errors import ToolError
from src.tools.materials import FaultInjector, MaterialsTool
from src.tools.rules import check_rules
from src.trace import TraceRecorder

MAX_STEPS = 20
MAX_TOOL_CALLS = 24
MAX_QUERY_REWRITES = 2
MAX_DRAFT_WRITES = 4
MAX_ACTION_REPAIRS = 2


class ModelError(Exception):
    pass


_STOP_REASON_ALIASES = {
    "no_materials_available": "insufficient_material",
    "no_material": "insufficient_material",
    "duration_below_min": "duration_cannot_meet",
    "duration_below_min_and_no_draft_writes_left": "duration_cannot_meet",
    "duration_over_max": "duration_cannot_meet",
    "draft_writes_left=0 且时长检查未通过": "duration_cannot_meet",
    "rules_failed": "rules_cannot_meet",
}


def _normalize_stop_reason(status: str, stop_reason: Optional[str]) -> Optional[str]:
    if status == "completed":
        return None
    if not stop_reason:
        return "insufficient_material" if status == "needs_input" else stop_reason
    return _STOP_REASON_ALIASES.get(str(stop_reason), stop_reason)


def _terminal(status: str, stop_reason: Optional[str], message: str = "", **extra: Any) -> Dict[str, Any]:
    data = {
        "status": status,
        "stop_reason": stop_reason,
        "message": message,
        "exit_code": exit_code_for(status),
        "limits": {"max_steps": MAX_STEPS, "max_tool_calls": MAX_TOOL_CALLS},
    }
    if status == "incomplete":
        data.setdefault("last_state", {"draft_revision": None, "checks": None})
    data.update(extra)
    return data


def _rev_diff(previous: Optional[Dict[str, Any]], current: Dict[str, Any],
              prev_rev: int, rev: int) -> Dict[str, Any]:
    prev_shots = {s.get("id"): s for s in (previous or {}).get("shots", [])}
    cur_shots = {s.get("id"): s for s in current.get("shots", [])}
    removed = [sid for sid in prev_shots if sid not in cur_shots]
    added = [sid for sid in cur_shots if sid not in prev_shots]
    changed = []
    for sid in cur_shots:
        if sid in prev_shots and prev_shots[sid] != cur_shots[sid]:
            changed.append({
                "id": sid,
                "before": prev_shots[sid].get("narration", ""),
                "after": cur_shots[sid].get("narration", ""),
            })
    return {"from": prev_rev, "to": rev, "removed_shots": removed,
            "added_shots": added, "changed_shots": changed}


class Orchestrator:
    def __init__(self, brief: Dict[str, Any], provider: Any):
        self.brief = brief
        self.provider = provider
        self.materials = load_json(DATA_DIR / "materials.json")
        self.rules_config = load_json(DATA_DIR / "brand_rules.json")
        self.materials_tool = MaterialsTool(self.materials, FaultInjector(brief.get("faults")))
        self.allowed_ids = brief.get("material_ids") or [m["id"] for m in self.materials]
        self.visible_materials = [m for m in self.materials if m["id"] in self.allowed_ids]
        self.state: Dict[str, Any] = {
            "brief": brief,
            "materials": [],
            "allowed_materials": self.visible_materials,
            "current_draft": None,
            "draft_revision": 0,
            "draft_hash": None,
            "last_estimate": None,
            "last_checks": {"duration": None, "rules": None, "citations": None},
            "last_observation": {"ok": True, "error_code": None},
            "search_attempts": 0,
            "tool_calls": 0,
            "draft_writes": 0,
            "action_repairs": 0,
            "revisions": [],
            "step": 0,
            "trace_errors": [],
        }
        self.trace = TraceRecorder(
            provider=provider.name,
            model=provider.model,
            mode=provider.mode,
            limits={"max_steps": MAX_STEPS, "max_tool_calls": MAX_TOOL_CALLS},
        )
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:6]

    def _record_error(self, code: str, message: str) -> None:
        self.state["trace_errors"].append({"code": code, "message": message})

    def _execute_tool(self, action: Dict[str, Any]) -> Dict[str, Any]:
        name = action["name"]
        args = action.get("args", {})
        self.state["tool_calls"] += 1

        if name == "search_materials":
            if self.state["search_attempts"] >= 1 + MAX_QUERY_REWRITES:
                self._record_error("QUERY_REWRITE_LIMIT", "查询改写超过上限")
                return {"ok": False, "error_code": "QUERY_REWRITE_LIMIT",
                        "message": "查询改写超过 %d 次" % MAX_QUERY_REWRITES, "retryable": False}
            self.state["search_attempts"] += 1
            try:
                result = self.materials_tool.search(
                    str(args.get("query") or ""),
                    int(args.get("top_k") or 5),
                    self.allowed_ids,
                )
            except ToolError as exc:
                self._record_error(exc.code, exc.message)
                return exc.to_observation()
            self.state["materials"] = result.get("items", [])
            result["empty"] = len(result.get("items", [])) == 0
            return result

        if name == "write_draft":
            if self.state["draft_writes"] >= MAX_DRAFT_WRITES:
                self._record_error("DRAFT_WRITE_LIMIT", "草稿写入超过上限")
                return {"ok": False, "error_code": "DRAFT_WRITE_LIMIT",
                        "message": "最多写入 %d 次草稿" % MAX_DRAFT_WRITES, "retryable": False}
            draft = {"title": args.get("title"), "shots": args.get("shots")}
            errors = validate_draft(draft)
            if errors:
                return {"ok": False, "error_code": "DRAFT_SCHEMA", "errors": errors, "retryable": True}
            known = set(m["id"] for m in self.visible_materials) | {"BRIEF"}
            for shot in draft["shots"]:
                for claim in shot.get("claims", []):
                    if claim.get("source_id") not in known:
                        return {"ok": False, "error_code": "UNKNOWN_SOURCE",
                                "message": "未知来源: " + str(claim.get("source_id")),
                                "retryable": True}
            prev = self.state["current_draft"]
            prev_rev = self.state["draft_revision"]
            rev = prev_rev + 1
            h = draft_hash(draft)
            diff = _rev_diff(prev, draft, prev_rev, rev)
            self.state["current_draft"] = draft
            self.state["draft_revision"] = rev
            self.state["draft_hash"] = h
            self.state["last_estimate"] = None
            self.state["last_checks"] = {"duration": None, "rules": None, "citations": None}
            self.state["draft_writes"] += 1
            self.state["revisions"].append({"revision": rev, "draft": copy.deepcopy(draft), "diff": diff})
            return {"ok": True, "revision": rev, "draft_hash": h, "diff": diff}

        if name == "estimate_duration":
            draft = self.state["current_draft"]
            if not draft:
                return {"ok": False, "error_code": "DRAFT_REQUIRED", "message": "请先写草稿", "retryable": True}
            est = estimate_draft(draft, float(self.brief["target_duration_sec"]))
            est["revision"] = self.state["draft_revision"]
            est["draft_hash"] = self.state["draft_hash"]
            self.state["last_estimate"] = est
            self.state["last_checks"]["duration"] = est
            return {"ok": True, **est}

        if name == "check_rules":
            draft = self.state["current_draft"]
            est = self.state["last_estimate"]
            if not draft:
                return {"ok": False, "error_code": "DRAFT_REQUIRED", "message": "请先写草稿", "retryable": True}
            if not est or est.get("revision") != self.state["draft_revision"] or est.get("draft_hash") != self.state["draft_hash"]:
                return {"ok": False, "error_code": "ESTIMATE_REQUIRED",
                        "message": "请先对当前 revision 估算时长", "retryable": True}
            try:
                result = check_rules(
                    draft, self.brief["brand_rule_set"], est,
                    self.rules_config,
                    {m["id"]: m for m in self.visible_materials},
                )
            except ToolError as exc:
                return exc.to_observation()
            result["revision"] = self.state["draft_revision"]
            result["draft_hash"] = self.state["draft_hash"]
            self.state["last_checks"]["rules"] = result
            return {"ok": True, **result}

        if name == "check_citations":
            draft = self.state["current_draft"]
            if not draft:
                return {"ok": False, "error_code": "DRAFT_REQUIRED", "message": "请先写草稿", "retryable": True}
            result = check_citations(draft, self.visible_materials, self.brief)
            result["revision"] = self.state["draft_revision"]
            result["draft_hash"] = self.state["draft_hash"]
            self.state["last_checks"]["citations"] = result
            return {"ok": True, **result}

        return {"ok": False, "error_code": "UNKNOWN_ACTION", "message": "未知动作", "retryable": False}

    def _required_missing(self) -> List[str]:
        missing = []
        st = self.state
        if not st["current_draft"]:
            missing.append("draft")
        if not st["last_estimate"] or st["last_estimate"].get("draft_hash") != st["draft_hash"]:
            missing.append("duration")
        rules = st["last_checks"].get("rules")
        if not rules or rules.get("draft_hash") != st["draft_hash"]:
            missing.append("rules")
        citations = st["last_checks"].get("citations")
        if not citations or citations.get("draft_hash") != st["draft_hash"]:
            missing.append("citations")
        return missing

    def _validate_finish(self, action: Dict[str, Any]) -> Tuple[bool, List[str]]:
        args = action.get("args", {})
        status = args.get("status")
        st = self.state
        if st["tool_calls"] == 0 and st["draft_writes"] == 0 and status != "needs_input":
            return False, ["no_action_evidence"]
        if status == "completed":
            missing = self._required_missing()
            if missing:
                return False, missing
            if not st["last_estimate"].get("pass"):
                missing.append("duration_not_pass")
            rules = st["last_checks"]["rules"]
            if not rules.get("pass"):
                missing.append("rules_not_pass")
            if rules.get("needs_review"):
                missing.append("needs_review")
            citations = st["last_checks"]["citations"]
            if not citations.get("pass"):
                missing.append("citations_not_pass")
            if self.brief.get("product_name") or self.brief.get("material_ids"):
                has_claim = any(
                    shot.get("claims")
                    for shot in (st["current_draft"] or {}).get("shots", [])
                )
                if not has_claim:
                    missing.append("no_product_claim")
            return len(missing) == 0, missing

        stop_reason = args.get("stop_reason") or ""
        if not stop_reason:
            return False, ["stop_reason_required"]
        if status == "needs_input":
            if not (args.get("missing_fields") or (st["search_attempts"] > 0 and st["last_observation"].get("empty"))):
                return False, ["missing_fields_or_empty_search_required"]
            return True, []
        if status == "unmet_constraints":
            if not (st["last_estimate"] or st["last_checks"].get("rules")):
                return False, ["check_before_unmet_required"]
            if not args.get("blocking_reason"):
                return False, ["blocking_reason_required"]
            return True, []
        if status == "incomplete":
            if stop_reason == "tool_unavailable" and not st["trace_errors"]:
                return False, ["tool_error_evidence_required"]
            return True, []
        if status == "failed":
            if not args.get("error_code"):
                return False, ["error_code_required"]
            return True, []
        return False, ["invalid_status"]

    def _shots_with_timing(self) -> List[Dict[str, Any]]:
        draft = self.state["current_draft"] or {}
        est = self.state["last_estimate"] or {}
        by_id = {s.get("id"): s for s in est.get("shots", [])}
        shots = []
        for shot in draft.get("shots", []):
            item = copy.deepcopy(shot)
            timing = by_id.get(shot.get("id"), {})
            item["start_sec"] = timing.get("start_sec")
            item["duration_sec"] = timing.get("duration_sec")
            item["source_ids"] = sorted({c.get("source_id") for c in shot.get("claims", []) if c.get("source_id")})
            shots.append(item)
        return shots

    def _sources(self) -> List[Dict[str, Any]]:
        by_id = {m["id"]: m for m in self.visible_materials}
        used: Dict[str, List[str]] = {}
        for shot in (self.state["current_draft"] or {}).get("shots", []):
            for claim in shot.get("claims", []):
                sid = claim.get("source_id")
                used.setdefault(sid, [])
                if shot.get("id") not in used[sid]:
                    used[sid].append(shot.get("id"))
        out = []
        for sid, ids in used.items():
            base = by_id.get(sid, {"id": "BRIEF", "text": self.brief.get("product_name", ""), "source_type": "user_input"})
            out.append({"id": sid, "used_in": ids, "text": base.get("text", "")})
        return out

    def _risks(self) -> List[Dict[str, str]]:
        risks = []
        if len(self.visible_materials) <= 1:
            risks.append({"code": "LIMITED_MATERIAL", "severity": "warn",
                          "message": "可用产品素材很少，脚本以使用建议为主。"})
        if not any(m.get("source_type") == "data" for m in self.visible_materials):
            risks.append({"code": "NO_EFFECT_DATA", "severity": "info",
                          "message": "未提供效果数据，脚本不包含效果提升结论。"})
        for err in self.state["trace_errors"]:
            risks.append({"code": err["code"], "severity": "error", "message": err["message"]})
        return risks

    def _finalize(self, action: Dict[str, Any], status: str, stop_reason: Optional[str]) -> Dict[str, Any]:
        st = self.state
        args = action.get("args", {})
        draft = st["current_draft"] or {}
        est = st["last_estimate"] or {}
        stop_reason = _normalize_stop_reason(status, stop_reason)
        question = args.get("question")
        if status == "needs_input" and not question:
            missing = args.get("missing_fields") or []
            question = "请补充：" + "、".join(str(x) for x in missing) if missing else "请补充必要信息后重试。"
        checks = {
            "duration": st["last_checks"].get("duration"),
            "rules": st["last_checks"].get("rules"),
            "citations": st["last_checks"].get("citations"),
        }
        result = {
            "run_id": self.run_id,
            "provider": self.provider.name,
            "model": self.provider.model,
            "mode": self.provider.mode,
            "status": status,
            "stop_reason": stop_reason,
            "exit_code": exit_code_for(status),
            "title": draft.get("title") or "未生成标题",
            "target_duration_sec": self.brief.get("target_duration_sec"),
            "estimated_total_sec": est.get("total_sec"),
            "estimator": {
                "version": est.get("version"),
                "cps": est.get("cps"),
                "subtitle_cps": est.get("subtitle_cps"),
                "pause_per_shot": est.get("pause_per_shot"),
            } if est else None,
            "assumptions": self.brief.get("assumptions", []),
            "limits": {"max_steps": MAX_STEPS, "max_tool_calls": MAX_TOOL_CALLS},
            "draft_revision": st["draft_revision"],
            "draft_hash": st["draft_hash"],
            "shots": self._shots_with_timing(),
            "sources": self._sources(),
            "checks": checks,
            "risks": self._risks(),
            "message": args.get("summary") or "",
            "question": question,
            "missing_fields": args.get("missing_fields", []),
            "blocking_reason": args.get("blocking_reason"),
            "options": args.get("options", []),
        }
        if status == "incomplete":
            result["last_state"] = {
                "draft_revision": st["draft_revision"],
                "checks": {
                    "duration": bool(st["last_checks"].get("duration")),
                    "rules": bool(st["last_checks"].get("rules")),
                    "citations": bool(st["last_checks"].get("citations")),
                },
            }
        if status == "failed":
            result["error_code"] = args.get("error_code") or "failure"
        return result

    def run(self) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
        prev_trace_index: Optional[int] = None
        for step in range(1, MAX_STEPS + 1):
            self.state["step"] = step
            try:
                raw = self.provider.decide(self.state)
                action, errors = parse_action(raw)
            except Exception as exc:
                msg = "模型调用失败: " + str(exc)
                self._record_error("MODEL_ERROR", msg)
                idx = self.trace.add(step, "", "model_error", {"ok": False, "error": msg},
                                     self.state["draft_revision"], self.state["draft_hash"])
                if prev_trace_index is not None:
                    self.trace.set_next(prev_trace_index, "model_error")
                self.trace.finalize("failed", "model_error", self.state["tool_calls"])
                result = _terminal("failed", "model_error", msg, run_id=self.run_id,
                                   provider=self.provider.name, model=self.provider.model,
                                   mode=self.provider.mode, exit_code=5, error_code="MODEL_ERROR")
                return result, self.trace.to_dict(), self.state["revisions"]

            if prev_trace_index is not None:
                self.trace.set_next(prev_trace_index, action.get("name") if action else "parse_error")

            if errors:
                self.state["action_repairs"] += 1
                obs = {"ok": False, "error_code": "INVALID_ACTION", "errors": errors}
                idx = self.trace.add(step, "", "parse_error", obs,
                                     self.state["draft_revision"], self.state["draft_hash"])
                prev_trace_index = idx
                if self.state["action_repairs"] > MAX_ACTION_REPAIRS:
                    self.trace.finalize("incomplete", "invalid_action_limit", self.state["tool_calls"])
                    result = _terminal("incomplete", "invalid_action_limit",
                                       "动作解析失败超过上限", run_id=self.run_id,
                                       provider=self.provider.name, model=self.provider.model,
                                       mode=self.provider.mode, exit_code=4)
                    return result, self.trace.to_dict(), self.state["revisions"]
                self.state["last_observation"] = obs
                continue

            if action["name"] == "finish":
                ok, missing = self._validate_finish(action)
                obs = {"ok": ok, "missing": missing}
                idx = self.trace.add(step, action.get("rationale", ""), action, obs,
                                     self.state["draft_revision"], self.state["draft_hash"])
                prev_trace_index = idx
                if not ok:
                    self.state["last_observation"] = {"ok": False, "error_code": "CHECKS_REQUIRED", "missing": missing}
                    continue
                status = action["args"]["status"]
                stop_reason = action["args"].get("stop_reason")
                self.trace.finalize(status, stop_reason, self.state["tool_calls"])
                result = self._finalize(action, status, stop_reason)
                return result, self.trace.to_dict(), self.state["revisions"]

            if self.state["tool_calls"] >= MAX_TOOL_CALLS:
                self.trace.add(step, action.get("rationale", ""), action,
                               {"ok": False, "error_code": "TOOL_CALL_LIMIT"},
                               self.state["draft_revision"], self.state["draft_hash"])
                self.trace.finalize("incomplete", "tool_call_limit_reached", self.state["tool_calls"])
                result = _terminal("incomplete", "tool_call_limit_reached",
                                   "工具调用达到上限", run_id=self.run_id,
                                   provider=self.provider.name, model=self.provider.model,
                                   mode=self.provider.mode, exit_code=4)
                return result, self.trace.to_dict(), self.state["revisions"]

            observation = self._execute_tool(action)
            self.state["last_observation"] = observation
            idx = self.trace.add(step, action.get("rationale", ""), action, observation,
                                 self.state["draft_revision"], self.state["draft_hash"])
            prev_trace_index = idx

        self.trace.finalize("incomplete", "step_limit_reached", self.state["tool_calls"])
        result = _terminal("incomplete", "step_limit_reached",
                           "已达到 %d 步执行上限" % MAX_STEPS, run_id=self.run_id,
                           provider=self.provider.name, model=self.provider.model,
                           mode=self.provider.mode, exit_code=4,
                           last_state={"draft_revision": self.state["draft_revision"]})
        return result, self.trace.to_dict(), self.state["revisions"]


def run_case(raw_input: Dict[str, Any], provider: Any) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    brief, errors = normalize_brief(raw_input)
    if errors:
        fields = [e["field"] for e in errors]
        question = "请补充：" + "、".join(fields)
        result = _terminal(
            "needs_input", "missing_required_fields", question,
            run_id="preflight-" + uuid.uuid4().hex[:6], provider=provider.name,
            model=provider.model, mode=provider.mode, exit_code=2,
            missing_fields=fields, question=question, assumptions=brief.get("assumptions", []),
            target_duration_sec=brief.get("target_duration_sec"),
            title="未生成标题", shots=[], sources=[], checks={}, risks=[],
        )
        trace = TraceRecorder(provider.name, provider.model, provider.mode,
                              {"max_steps": MAX_STEPS, "max_tool_calls": MAX_TOOL_CALLS})
        trace.add(0, "输入缺少必填字段，前置校验终止", "preflight", {"ok": False, "missing": fields}, 0, None)
        trace.finalize("needs_input", "missing_required_fields", 0)
        return result, trace.to_dict(), []
    return Orchestrator(brief, provider).run()
