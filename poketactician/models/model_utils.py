def process_items(items, check_function):
    if isinstance(items[0], str):
        # It's a list of strings
        check_function(items)
    elif isinstance(items[0], list):
        # It's a list of lists of strings
        for sublist in items:
            check_function(sublist)
    else:
        raise ValueError("Invalid input format.")
