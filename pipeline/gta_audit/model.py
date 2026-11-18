"""The formulas. No numeric defaults anywhere: every number comes from the dataset or a
labeled convention in model_frozen.json. A missing input never gets estimated."""
from .errors import MissingInputError, SanityError


# ---- formulas (pure; every argument required) ---------------------------------------------

def claim_reproduction(workers, output_per_day):
    return workers * output_per_day


def output_per_day_base(avg_annual_output, working_days):
    return avg_annual_output / working_days


def output_per_day_gdp(gdp, employed, working_days):
    return gdp / employed / working_days


def absences_low(employed, baseline_rate, lift):
    """Additional absences: the normal daily absence rate, lifted by the measured PTO-request increase."""
    return employed * baseline_rate * lift


def absences_high(population, skip_rate):
    return population * skip_rate


def cost(absences, output_per_day):
    return absences * output_per_day


def check_claim(reproduced, expected, tolerance_pct):
    if abs(reproduced - expected) > expected * tolerance_pct / 100.0:
        raise SanityError(f"claim reproduction failed: inputs give {reproduced:,.0f}, "
                          f"expected {expected:,.0f} (tolerance {tolerance_pct}%)")


def check_cap(high_absences, superbowl_absences):
    if not high_absences < superbowl_absences:
        raise SanityError(f"sanity cap failed: high-case absences {high_absences:,.0f} are not below "
                          f"Super Bowl Monday absences {superbowl_absences:,.0f}; the high case is "
                          "implausible as specified and the build stops")


# ---- wiring -------------------------------------------------------------------------------

def _convention(config, name):
    try:
        return config["conventions"][name]["value"]
    except KeyError:
        raise MissingInputError(f"config convention {name!r} missing")


def _inputs(dataset, mapping):
    """Resolve {name: dataset_id}; return (values, missing_ids)."""
    values, missing = {}, []
    for name, rid in mapping.items():
        fig = dataset.get(rid)
        if fig is None or fig.get("value") is None:
            missing.append(rid)
        else:
            values[name] = fig["value"]
    return values, missing


def _section(inputs, missing, **values):
    return {"status": "insufficient" if missing else "complete",
            "inputs": inputs, "missing": sorted(set(missing)), **(values if not missing else {})}


def compute(config, dataset):
    """Compute every section. Missing inputs mark a section 'insufficient' (never filled in).
    Sanity checks raise SanityError whenever their inputs are present."""
    wd = _convention(config, "working_days_per_year")
    tol = _convention(config, "claim_reproduction_tolerance_pct")
    r = {"conventions": {"working_days_per_year": wd, "claim_reproduction_tolerance_pct": tol}}

    ca = config["claim_audit"]
    v, miss = _inputs(dataset, ca["inputs"])
    if not miss:
        rep = claim_reproduction(v["workers"], v["output_per_day"])
        check_claim(rep, ca["expected_reproduction_usd"], tol)
        r["claim_audit"] = _section(ca["inputs"], miss, headline_usd=v["headline_usd"], reproduced_usd=rep,
                                    expected_reproduction_usd=ca["expected_reproduction_usd"],
                                    gap_usd=v["headline_usd"] - rep)
    else:
        r["claim_audit"] = _section(ca["inputs"], miss)

    opw = config["output_per_worker_day"]
    v, miss = _inputs(dataset, opw["base"]["inputs"])
    base = _section(opw["base"]["inputs"], miss,
                    **({"usd_per_day": output_per_day_base(v["avg_annual_output"], wd)} if not miss else {}))
    v, miss = _inputs(dataset, opw["sensitivity"]["inputs"])
    sens = _section(opw["sensitivity"]["inputs"], miss,
                    **({"usd_per_day": output_per_day_gdp(v["gdp"], v["employed"], wd)} if not miss else {}))
    r["output_per_worker_day"] = {"base": base, "sensitivity": sens}

    ac = config["absence_cases"]
    v, miss_low = _inputs(dataset, ac["low"]["inputs"])
    low = _section(ac["low"]["inputs"], miss_low,
                   **({"absences": absences_low(v["employed"], v["baseline_rate"], v["lift"])} if not miss_low else {}))
    v, miss_high = _inputs(dataset, ac["high"]["inputs"])
    high = _section(ac["high"]["inputs"], miss_high,
                    **({"absences": absences_high(v["population"], v["skip_rate"])} if not miss_high else {}))
    r["absence_cases"] = {"status": "insufficient" if (miss_low or miss_high) else "complete",
                          "missing": sorted(set(miss_low + miss_high)), "low": low, "high": high}

    costs = {}
    for case in config["costs"]["cases"]:
        for rate in config["costs"]["rates"]:
            a, o = r["absence_cases"][case], r["output_per_worker_day"][rate]
            miss = a["missing"] + o["missing"]
            costs[f"{case}_{rate}"] = _section({"case": case, "rate": rate}, miss,
                                               **({"usd": cost(a["absences"], o["usd_per_day"])} if not miss else {}))
    r["costs"] = costs

    sb = config["benchmarks"]["superbowl"]
    v, miss = _inputs(dataset, sb["inputs"])
    rate_sec = r["output_per_worker_day"][sb["dollar_equivalent_rate"]]
    sb_vals = {}
    if not miss:
        sb_vals["absences"] = v["absences"]
        if high["status"] == "complete":
            check_cap(high["absences"], v["absences"])
            sb_vals["cap_check"] = "passed"
        if rate_sec["status"] == "complete":
            sb_vals["dollar_equivalent_usd"] = cost(v["absences"], rate_sec["usd_per_day"])
    # Absences and the dollar equivalent are both required (decision 7): the section is complete
    # only when both exist. Partial values (e.g. absences without a rate) are kept for the record.
    sb_missing = sorted(set(miss + ([] if miss else rate_sec["missing"])))
    superbowl = {"status": "insufficient" if sb_missing else "complete",
                 "inputs": sb["inputs"], "missing": sb_missing, **sb_vals}

    pc = config["benchmarks"]["precedent_gtav_2013"]
    row = dataset.get(pc["row"])
    if row is not None and row.get("value") is not None and row.get("kind") == pc["required_kind"]:
        precedent = {"status": "complete", "rendered": True, "row": pc["row"], "value": row["value"],
                     "wording": pc["wording"], "missing": []}
    else:
        precedent = {"status": "omitted", "rendered": False, "row": pc["row"], "missing": [pc["row"]],
                     "reason": "no sourced precedent row in the dataset; section omitted by design"}
    r["benchmarks"] = {"superbowl": superbowl, "precedent_gtav_2013": precedent}

    def present(ids):
        return {i: dataset[i]["value"] for i in ids if i in dataset and dataset[i].get("value") is not None}

    for group, ids in (("context", config["context"]["survey_intent"]),
                       ("anchors", config["anchors"]["optional"]),
                       ("proxies", config["proxies"]["optional"])):
        got = present(ids)
        r[group] = {"present": got, "missing": [i for i in ids if i not in got]}
    return r


def _lookup(results, dotted):
    node = results
    for part in dotted.split("."):
        node = node[part]
    return node


def core_missing(config, results):
    """{section: [missing ids]} for every required_for_render section that is incomplete."""
    out = {}
    for sec in config["required_for_render"]:
        node = _lookup(results, sec)
        if node.get("status") != "complete":
            out[sec] = node.get("missing", [])
    return out


def require_core(config, results):
    missing = core_missing(config, results)
    if missing:
        lines = [f"{sec}: missing {ids}" for sec, ids in missing.items()]
        raise MissingInputError("core sections incomplete:\n  " + "\n  ".join(lines))
