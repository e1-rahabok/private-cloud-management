"""Agent E2 drafts for PCM (D-076).

GENERATED from spec/catalog/settings.yaml (agent_e2.*), spec/workspaces/noc/incident.md and spec/workspaces/l2/frame.md.
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
    "rca_draft": ("Draft a root cause analysis for an L2 engineer, from the evidence and the investigation: the root cause, "
                  "the corrective action that prevents a repeat, and how the next occurrence will be detected (a check rule, "
                  "an alert, or an SOP for L1). Raw counters are allowed here. Separate what is proven from what is assumed."),
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
    """NOC incident drafts. Returns {text, source, model}."""
    return draft_facts(facts_for(detail), task, settings, avoided, fallback(detail))


def draft_facts(facts: dict, task: str, settings: dict, avoided: list, template: str) -> dict:
    """Returns {text, source, model}. source: model, fallback_vocabulary or fallback_unavailable."""
    model = settings["agent_e2.model"]
    if settings.get("agent_e2.mode") == "mock" or os.environ.get("PCM_AGENT_E2_MODE") == "mock":
        return {"text": "Draft by Agent E2, to review (mock): " + template.split(": ", 1)[-1],
                "source": "model", "model": "mock"}
    key = os.environ.get(settings["agent_e2.api_key_env"])
    if not key:
        return {"text": template, "source": "fallback_unavailable", "model": model}
    system = SYSTEM.format(avoided=", ".join(avoided))
    if task == "rca_draft":  # L2 reads raw counters (L2 vocabulary); the L1 rule against units does not apply
        system = system.replace("- Scores are from 0 to 100. Do not use raw counters or units such as milliseconds.\n", "")
        system = system.replace("You help a Level 1 NOC operator.", "You help a Level 2 platform engineer.")
        system = system.replace("At most 6 sentences.", "At most 10 sentences.")
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": TASKS[task] + "\n\nFacts (JSON):\n" + json.dumps(facts, indent=1, default=str)}]
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
        return {"text": template, "source": "fallback_vocabulary", "model": model}
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError):
        return {"text": template, "source": "fallback_unavailable", "model": model}


def ask_service(url: str, question: str, facts: dict, role: str, timeout: int = 180, turns: list | None = None) -> dict:
    """Agent E2 service (D-078): the knowledge base, the reading plan and the model call, behind one endpoint.
    turns: a clarifying round, [first question, Agent E2's questions, the reply]; the facts go with the first.
    Returns {type, content, questions, files_read, lead, computed, model, knowledge_commit, source}. lead: the opening the
    person reads first, in plain words (D-119); computed: the calculator's lines, kept for review, not shown.
    source: service; model_unavailable (the service answered 502: its model cannot be reached); unavailable (no service)."""
    body = {"question": question, "facts": facts, "role": role}
    if turns:
        body["turns"] = turns
    try:
        out = _post_raw(url.rstrip("/") + "/v1/answer", body, timeout)
        return {"content": out.get("content") or "", "lead": out.get("lead") or "", "questions": out.get("questions", []), "type": out.get("type"),
                "files_read": out.get("files_read", []), "computed": out.get("computed", []),
                "model": out.get("model"), "knowledge_commit": out.get("knowledge_commit"), "source": "service"}
    except urllib.error.HTTPError as e:
        # The service answered, but its model did not (502): say which part is down (frame.md, Agent E2 panel).
        return {"type": None, "content": "", "questions": [], "files_read": [], "lead": "", "computed": [], "model": None,
                "knowledge_commit": None, "source": "model_unavailable" if e.code == 502 else "unavailable"}
    except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, KeyError):
        return {"type": None, "content": "", "questions": [], "files_read": [], "lead": "", "computed": [], "model": None,
                "knowledge_commit": None, "source": "unavailable"}


def suggest_service(url: str, facts: dict, timeout: int = 5) -> dict:
    """Agent E2's suggested questions for a whole page, chosen by the page's situation (D-123). No model call on its side,
    so a short wait. Returns {questions, situation, source}; questions is empty when Agent E2 has none for the page or does
    not answer, and the panel then keeps the general questions."""
    try:
        out = _post_raw(url.rstrip("/") + "/v1/suggest", {"facts": facts}, timeout)
        return {"questions": [q for q in out.get("questions") or [] if isinstance(q, str)][:3], "situation": out.get("situation"),
                "source": "service"}
    except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, KeyError):
        return {"questions": [], "situation": None, "source": "unavailable"}


def _post_raw(url: str, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body, default=str).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

