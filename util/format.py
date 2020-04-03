
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
        round1 = int(number*10) / 10
        if round1 == number:
            return f"{round1:.1f}"
        else:
            number = int(number*100) / 100
            return f"{number:.2f}"

    if number < 10:
        if int(number) == number:
            return f"{number:.0f}"

        number = int(number*10) / 10
        return f"{number:.1f}"

    return f"{number:,.0f}"

