def get_dashboard_data(data):
    data["transactions"].append({"label": None, "items": ["Integration Request"]})

    non_standard_fieldnames = data.setdefault("non_standard_fieldnames", {})

    non_standard_fieldnames.update(
        {
            "Integration Request": "reference_docname",
        }
    )

    return data
