def remove_duplicates_from_list(input_list):
    return list(set(input_list))

def remove_duplicates_from_dict_list(input_list):
    unique_dicts = []
    for item in input_list:
        # Convert dict to a tuple to use as a key in a dict
        item_tuple = tuple(item.items())
        if item_tuple not in (d.items() for d in unique_dicts):
            unique_dicts.append(item)
    return unique_dicts