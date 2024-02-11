def merge_filters(old_list, new_list):
    old_list = old_list.copy()
    for new_filter in new_list:
        if new_filter["type"] in [old_filter["type"] for old_filter in old_list]:
            old_filter = next(el for el in old_list if el["type"] == new_filter["type"])
            for value in new_filter["values"]:
                if value not in old_filter["values"]:
                    old_filter["values"].append(value)
        else:
            old_list.append(new_filter)
    return old_list


def generate_all_possible_filters(filter_):
    out = []
    for value in filter_["values"]:
        new_filter = filter_.copy()
        new_filter["values"] = [value]
        out.append([new_filter])
    return out