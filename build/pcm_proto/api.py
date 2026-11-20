"""Executive API responses, shaped by spec/api/openapi.yaml.

GENERATED. Do not edit by hand (D-070). Every value carries its metadata (PCM core, 3.5).
"""
from __future__ import annotations

from datetime import datetime

from . import catalog

V = catalog.DEFINITION_VERSION
RES_WORDS = {"compute": "computing power", "memory": "working memory", "storage": "storage"}


def meta(definition: str, as_of: datetime, source: str, stale: bool = False) -> dict:
    return {"definition": definition, "definition_version": V, "as_of": as_of.isoformat(),
            "source": source, "stale": stale}


def num(value, definition, as_of, source, unit=None, status=None, stale=False) -> dict:
    out = {"value": None if stale else value, "meta": meta(definition, as_of, source, stale)}
    if unit:
        out["unit"] = unit
    if status:
        out["status"] = "no_data" if stale else status
    return out


def date_value(dt: datetime, now: datetime, definition, source, status=None, stale=False) -> dict:
    out = {"value": None if stale else dt.date().isoformat(),
           "days_from_now": None if stale else (dt.date() - now.date()).days,
           "meta": meta(definition, now, source, stale)}
    if status:
        out["status"] = "no_data" if stale else status
    return out


def decision(ds: dict, lid: str) -> dict:
    loc = ds["locations"][lid]
    d = loc["decision"]
    return {"location": lid, "cluster_group": d["group"], "resource": d["resource"],
            "date": date_value(d["date"], ds["now"], "capacity.location_decision", loc["source"],
                               d["status"], loc["stale"]),
            "in_plan": d["in_plan"]}


def location_summary(ds: dict, lid: str) -> dict:
    loc, now = ds["locations"][lid], ds["now"]
    share = round(100.0 * loc["cores"] / ds["total_cores"], 1)
    return {"id": lid, "name": loc["name"],
            "share_percent": num(share, "scale.location_share_percent", now, "pcm", "percent"),
            "compute_cores": num(loc["cores"], "scale.compute_cores", loc["as_of"], loc["source"], "cores"),
            "in_use_percent": num(loc["in_use"]["compute"], "scale.in_use_percent", loc["as_of"],
                                  loc["source"], "percent", stale=loc["stale"]),
            "decision": decision(ds, lid), "stale": loc["stale"]}


def health_sentence(ds: dict, q: str) -> str:
    h = ds["health"][q]
    if q == "up":
        return f"Virtual machines were running {h['value']}% of the time they were meant to."
    if q == "fast":
        order = ("Gold scored above Silver, and Silver above Bronze, as promised." if h["order_kept"]
                 else "A lower class scored above a higher class, so the price difference is not being delivered.")
        return f"Virtual machines scored {round(h['value'])} out of 100 on performance. {order}"
    parts = []
    names = {lid: l["name"] for lid, l in ds["locations"].items()}
    for lid, b in h["below_by_location"].items():
        parts.append(f"{b['vms']} virtual machines in {names[lid]} fell below the security target this month: "
                     f"remote admin access was left open on their servers for {b['hours']} hours.")
    if h["certificates_expired"]:
        parts.append(f"{h['certificates_expired']} security certificates have expired.")
    if h["risk_certificates"]:
        parts.append(f"{h['risk_certificates']} security certificates expire within "
                     f"{ds['settings']['safe.certificate_warning_days']} days.")
    return " ".join(parts) or "No open findings this month."


def health_card(ds: dict, q: str) -> dict:
    now, st, h = ds["now"], ds["settings"], ds["health"][q]
    if q == "up":
        status = catalog.band_status(h["value"], st["up.target_percent"], st["up.amber_margin_percent"])
        defn = "up.availability_percent"
        card = {"headline": num(h["value"], defn, now, "vcf-operations", "percent", status)}
    elif q == "fast":
        defn = "fast.production_kpi"
        card = {"headline": num(h["value"], defn, now, "vcf-operations", "score", h["status"]),
                "class_kpi": {c: num(v, "fast.class_group_kpi", now, "vcf-operations", "score", catalog.kpi_band(v))
                              for c, v in h["class_kpi"].items()},
                "order_kept": h["order_kept"]}
    else:
        defn = "safe.ksi_percent"
        card = {"headline": num(h["value"], defn, now, "vcf-operations", "percent", h["status"]),
                "vms_below_sla": num(h["vms_below_sla"], "safe.vms_below_sla", now, "vcf-operations", "count"),
                "sla_contract_percent": st["safe.sla_contract_percent"],
                "open_findings": {k: num(h[k], f"safe.{k}", now, "vcf-operations", "count")
                                  for k in ("ssh_or_shell_enabled", "lockdown_off", "certificates_expired", "root_logins_open")},
                "risk_certificates": num(h["risk_certificates"], "safe.risk_certificates", now, "vcf-operations", "count")}
    card["sentence"] = health_sentence(ds, q)
    card["sparkline_7d"] = {"points": h["series7"], "meta": meta(defn, now, "vcf-operations")}
    return card


def summary(ds: dict) -> dict:
    now, locs = ds["now"], ds["locations"]
    fresh = [l for l in locs.values() if not l["stale"]]

    def weighted(res):
        w = sum(l["cores"] for l in fresh) or 1
        return round(sum(l["in_use"][res] * l["cores"] for l in fresh) / w, 1)

    est = min(locs, key=lambda k: locs[k]["decision"]["date"])
    v, rec = ds["value"], ds["recovery"]
    worst = sorted(rec, key=lambda r: {"red": 0, "amber": 1, "green": 2}[r["status"]])[0]
    oldest = min(l["as_of"] for l in locs.values())
    return {
        "updated_at": now.isoformat(),
        "oldest_data_at": oldest.isoformat(),
        "stale_locations": [l["id"] for l in locs.values() if l["stale"]],
        "scale": {
            "compute_cores": num(ds["total_cores"], "scale.compute_cores", now, "vcf-operations", "cores"),
            "memory_tb": num(round(sum(l["memory_tb"] for l in locs.values()), 1), "scale.memory_tb", now, "vcf-operations", "TB"),
            "storage_tb": num(round(sum(l["storage_tb"] for l in locs.values()), 1), "scale.storage_tb", now, "vcf-operations", "TB"),
            "in_use_percent": {r: {**num(weighted(r), "scale.in_use_percent", now, "vcf-operations", "percent"),
                                   "excludes": [l["id"] for l in locs.values() if l["stale"]]}
                               for r in ("compute", "memory", "storage")},
            "locations": [location_summary(ds, lid) for lid in locs],
        },
        "health": {q: health_card(ds, q) for q in ("up", "fast", "safe")},
        "room_to_grow": {
            "estate_decision": decision(ds, est),
            "next_round_closes_on": date_value(ds["next_round_closes"], now, "procurement_round.next", "capacity"),
        },
        "value": {
            "cost_annual": num(v["cost_annual"], "value.cost_annual", now, "cost-model", "USD"),
            "tco": num(v["tco"], "value.tco", now, "cost-model", "USD"),
            "public_cloud_difference_percent": num(v["difference_percent"], "value.public_cloud_comparison",
                                                   v["public_cloud_as_of"], "finops-input", "percent"),
            "cost_avoided_ytd": num(v["cost_avoided_ytd"], "value.cost_avoided_ytd", now, "capacity", "USD"),
            "site_recovery_status": worst["status"],
            "site_recovery_summary": recovery_sentence(ds, worst),
            "delivery_hours": num(ds["speed"]["now"], "speed.delivery_time", now, "vcf-automation", "hours"),
            "delivery_hours_year_ago": num(ds["speed"]["year_ago"], "speed.delivery_time", now, "vcf-automation", "hours"),
        },
        "goals": [{"id": g["id"], "title": g["title"],
                   "current": num(g["current"], "goals.status", now, "pcm"),
                   "target": g["target"], "direction": g["direction"], "status": g["status"]} for g in ds["goals"]],
    }


def recovery_sentence(ds: dict, r: dict) -> str:
    name = ds["locations"][r["location"]]["name"]
    months = max(1, round(r["days_ago"] / 30))
    if r["status"] == "green":
        return f"All site recovery plans were tested, most recently {name} {months} months ago, within target."
    untested = r["protected_vms"] - r["vms_in_test"]
    if r["status"] == "amber":
        return (f"{name}'s site recovery was last tested {months} months ago, "
                f"but {untested} virtual machines added since were not in the test.")
    return f"{name}'s site recovery is overdue for a test, or missed its target."


def location_detail(ds: dict, lid: str) -> dict:
    loc, now = ds["locations"][lid], ds["now"]
    st = ds["settings"]
    by = ds["health"]
    return {
        "location": location_summary(ds, lid),
        "memory_tb": num(loc["memory_tb"], "scale.memory_tb", loc["as_of"], loc["source"], "TB"),
        "storage_tb": num(loc["storage_tb"], "scale.storage_tb", loc["as_of"], loc["source"], "TB"),
        "in_use_by_resource": {r: num(loc["in_use"][r], "scale.in_use_percent", loc["as_of"], loc["source"],
                                      "percent", stale=loc["stale"]) for r in ("compute", "memory", "storage")},
        "health": {
            "up": "no_data" if loc["stale"] else catalog.band_status(by["up"]["by_location"][lid], st["up.target_percent"], st["up.amber_margin_percent"]),
            "fast": "no_data" if loc["stale"] else ("green" if catalog.kpi_band(by["fast"]["by_location"][lid]) == "green" else "amber"),
            "safe": "no_data" if loc["stale"] else ("red" if by["safe"]["by_location"].get(lid) else "green"),
        },
    }


def health_detail(ds: dict, q: str, window_days: int = 7) -> dict:
    now, st, h = ds["now"], ds["settings"], ds["health"][q]
    defn = {"up": "up.availability_percent", "fast": "fast.production_kpi", "safe": "safe.vms_below_sla"}[q]
    pts = h["series30"] if (window_days == 30 and "series30" in h) else h["series7"]
    out = {"question": q, "series": {"points": pts, "meta": meta(defn, now, "vcf-operations")},
           "by_location": [{"location": lid,
                            "value": num(h["by_location"][lid], defn, ds["locations"][lid]["as_of"],
                                         ds["locations"][lid]["source"], stale=ds["locations"][lid]["stale"])}
                           for lid in ds["locations"]],
           "events": h.get("events", [])}
    if q == "up":
        out["target"] = num(st["up.target_percent"], "setting up.target_percent", now, "settings", "percent")
    return out


def capacity_detail(ds: dict) -> dict:
    order = sorted(ds["locations"], key=lambda k: ds["locations"][k]["decision"]["date"])
    return {"locations": [decision(ds, lid) for lid in order],
            "next_round_closes_on": date_value(ds["next_round_closes"], ds["now"], "procurement_round.next", "capacity")}


def value_detail(ds: dict, card: str) -> dict:
    now, v = ds["now"], ds["value"]
    out = {"card": card}
    if card == "cost":
        out["cost"] = {
            "product": num(v["cost"]["product"], "value.cost_product", now, "cost-model", "USD"),
            "service": num(v["cost"]["service"], "value.cost_service", now, "cost-model", "USD"),
            "people": num(v["cost"]["people"], "value.cost_people", now, "cost-model", "USD"),
            "tco": num(v["tco"], "value.tco", now, "cost-model", "USD"),
            "public_cloud_estimate": num(v["public_cloud_estimate"], "value.public_cloud_comparison",
                                         v["public_cloud_as_of"], "finops-input", "USD"),
            "cost_avoided_ytd": num(v["cost_avoided_ytd"], "value.cost_avoided_ytd", now, "capacity", "USD"),
            "cost_avoidable_next_round": num(v["cost_avoidable_next_round"], "value.cost_avoidable_next_round", now, "capacity", "USD"),
        }
    elif card == "site_recovery":
        out["site_recovery"] = [{
            "location": r["location"],
            "last_test_at": date_value(r["last_test_at"], now, "recovery.last_test_at", "live-site-recovery"),
            "recovery_minutes": num(r["recovery_minutes"], "recovery.recovery_minutes", now, "live-site-recovery", "minutes"),
            "target_minutes": num(r["target_minutes"], "recovery.target_minutes", now, "live-site-recovery", "minutes"),
            "share_tested_percent": num(r["share_tested_percent"], "recovery.share_tested_percent", now, "live-site-recovery", "percent"),
            "status": r["status"]} for r in ds["recovery"]]
    elif card == "speed":
        out["speed"] = {"series_12m": {"points": ds["speed"]["series12"], "meta": meta("speed.delivery_time", now, "vcf-automation")}}
    return out
