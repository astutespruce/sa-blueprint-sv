
def format_number(number):
    """Format numbers for display.

    if < 1, return 2 decimal places
    if <10, return 1 decimal places
    otherwise, return comma formatted number with no decimal places

    Parameters
    ----------
    number : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    if number == 0:
        return "0"
    if number < 1:
        return f"{number:.2f}"
    if number < 10:
        return f"{number:.1f}"
    return f"{number:,.0f}"

