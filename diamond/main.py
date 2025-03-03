def create_diamond(width: int):
    """
    Creates diamond shape with clever way of handeling even number.
    Works perfectly for any positing number.
    """
    even = False
    if width % 2 == 0:
        even = True
        width += 1

    def getPattern(width: int, i: int):
        pattern = ("*" * i).center(width)
        if even and width == i:
            half = "*" * (i // 2)
            pattern = half + " " + half

        return pattern

    for i in range(1, width + 1, 2):
        p = getPattern(width, i)
        print(p)

    for i in range(width - 2, 0, -2):
        p = getPattern(width, i)
        print(p)

# create_diamond(6)
