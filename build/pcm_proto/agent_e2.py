"""Agent E2 drafts for PCM (D-076).

GENERATED from spec/catalog/settings.yaml (agent_e2.*) and spec/workspaces/noc/incident.md.
Do not edit by hand (D-070).

One OpenAI-compatible client. Demo: Vercel AI Gateway. Customer site: a local model server.
Agent E2 drafts; it never decides (NOC design, 3.8). Its words are checked like a page's (D-076).
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

SYSTEM = """You are Agent E2, a team member in the private cloud operations team. You help a Level 1 NOC operator.
Rules:
- Use only the facts given. If a fact is missing, say it is not known. Never invent a number, object or event.
- sop_steps lists what the SOP offers. An action in sop_steps is available, not done.
- Only actions_already_done were done. If it is empty, say that L1 has taken no action yet.
- You draft. You never decide severity, never choose an action outside the SOP, never close the incident.
- Write plain, short sentences for a junior operator. No headings. At most 6 sentences.
- Scores are from 0 to 100. Do not use raw counters or units such as milliseconds.
- Never use these words: {avoided}.
- Start with the most important fact."""

TASKS = {
    "explain": "Explain this incident to the operator: what is wrong, where, what the SOP checks found, and what the SOP says to do next.",
    "escalation_note": "Draft the escalation note to the L2 group named in escalation_route: what happened, the SOP steps run and their results, the villain and the victims, and what L1 already did.",
}


def _post(endpoint: str, key: str, body: dict, timeout: int = 60) -> dict:
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def avoided_found(text: str, avoided: list) -> list:
    return [w for w in avoided if re.search(rf"\b{re.escape(w)}\b", text, re.I)]


def facts_for(detail: dict) -> dict:
    """Only what the operator's page shows (PCM core, 3.12)."""
    keep = ("title", "root_object", "root_object_type", "location_name", "severity", "state", "alert_count",
            "escalation_route", "alerts")
    out = {k: detail.get(k) for k in keep}
    out["sop_steps"] = []
    for s in detail["sop"]["steps"]:
        step = {k: s.get(k) for k in ("kind", "text", "result", "passed")}
        if s.get("action"):
            step["available_action"] = {"action": s["action"], "target": s.get("target"),
                                        "allowed_for_l1": s.get("allowed"), "refusal": s.get("refusal") or None}
        out["sop_steps"].append(step)
    out["actions_already_done"] = [{k: h[k] for k in ("action", "target", "after")} for h in detail.get("history", [])
                                   if h["action"] != "agent_draft"]
    return out


def fallback(detail: dict) -> str:
    return detail["agent_draft"]


def draft(detail: dict, task: str, settings: dict, avoided: list) -> dict:
    """Returns {text, source, model}. source: model, fallback_vocabulary or fallback_unavailable."""
    model = settings["agent_e2.model"]
    if settings.get("agent_e2.mode") == "mock" or os.environ.get("PCM_AGENT_E2_MODE") == "mock":
        return {"text": "Draft by Agent E2, to review (mock): " + fallback(detail).split(": ", 1)[-1],
                "source": "model", "model": "mock"}
    key = os.environ.get(settings["agent_e2.api_key_env"])
    if not key:
        return {"text": fallback(detail), "source": "fallback_unavailable", "model": model}
    messages = [{"role": "system", "content": SYSTEM.format(avoided=", ".join(avoided))},
                {"role": "user", "content": TASKS[task] + "\n\nFacts (JSON):\n" + json.dumps(facts_for(detail), indent=1)}]
    try:
        for attempt in range(2):
            resp = _post(settings["agent_e2.endpoint"], key,
                         {"model": model, "messages": messages, "temperature": 0, "max_tokens": 600})
            text = (resp["choices"][0]["message"]["content"] or "").strip()
            bad = avoided_found(text, avoided)
            if text and not bad:
                return {"text": "Draft by Agent E2, to review: " + text, "source": "model", "model": model}
            messages += [{"role": "assistant", "content": text},
                         {"role": "user", "content": f"Rewrite without these words: {', '.join(bad) or 'none'}. Keep the same facts."}]
        return {"text": fallback(detail), "source": "fallback_vocabulary", "model": model}
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
        return {"text": fallback(detail), "source": "fallback_unavailable", "model": model}
