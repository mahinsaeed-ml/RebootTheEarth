def actions_from_signals(pests, trends, risk, cfg):
    acts = []
    if pests["whitefly"] >= cfg["pests"]["whitefly_warn"]:
        acts.append("Increase sticky traps and scout leaves.")
    if risk["vpd_band"] == "high":
        acts.append("Add shade cloth, increase cooling.")
    if not acts:
        acts.append("Conditions normal.")
    return acts
