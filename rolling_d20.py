import d20


def rolling_d20(content):

    content_split = content.split()
    if len(content_split) > 2 or len(content_split) < 2 :
        return "Please enter a roll in the format '!r **X**d**Y**' where **X** and **Y** are numbers"
    else:
        result = str(d20.roll(str(content_split[-1])))

    return result
