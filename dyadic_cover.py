"""Four-way subdivisions used by the two-dimensional certificates in Appendix D."""


def cover_cells(paths, context, max_depth=None):
    """Return (input index, x index, y index, level) for every leaf of a full cover.

    At level k, the cell with indices (i, j) has lower corner (i, j) / 2**k
    in the unit square. Digit 2*dx + dy selects the child with offsets (dx, dy).
    """
    root = {}
    for index, path in enumerate(paths):
        if not isinstance(path, str) or (max_depth is not None and len(path) > max_depth):
            raise ValueError(f"{context}: invalid subdivision path {path!r}")
        node = root
        for depth, digit in enumerate(path):
            if digit not in "0123":
                raise ValueError(f"{context}: invalid digit in path {path!r}")
            if None in node:
                raise ValueError(f"{context}: leaf {path[:depth]!r} also contains {path!r}")
            node = node.setdefault(digit, {})
        if node:
            raise ValueError(f"{context}: duplicate or overlapping leaf {path!r}")
        node[None] = index

    cells = []
    pending = [(root, "", 0, 0)]
    while pending:
        node, path, i, j = pending.pop()
        if None in node:
            cells.append((node[None], i, j, len(path)))
            continue
        missing = [digit for digit in "0123" if digit not in node]
        if missing:
            raise ValueError(f"{context}: cell {path or 'root'} is missing children {', '.join(missing)}")
        for digit in (3, 2, 1, 0):
            key = str(digit)
            pending.append((node[key], path + key, 2*i + digit//2, 2*j + digit%2))
    return cells
