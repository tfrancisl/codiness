def summarize_regions(regions: list[dict]) -> dict:
    """Total the sales of every active product, per region."""
    totals = {}
    for region in regions:
        for store in region["stores"]:
            if store["open"]:
                for sale in store["sales"]:
                    if sale["product"]["active"]:
                        totals[region["name"]] = totals.get(region["name"], 0) + sale["amount"]
    return totals
