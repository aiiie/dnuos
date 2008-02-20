"""Tools for compiling gettext catalogs"""

import array
import os
import struct


def _add(messages, id_, str_, fuzzy):
    """Add a non-fuzzy translation to the dictionary"""

    if not fuzzy and str_:
        messages[id_] = str_


def _generate(messages):
    """Return the generated output"""

    keys = messages.keys()
    # the keys are sorted in the .mo file
    keys.sort()
    offsets = []
    ids = ''
    strs = ''
    for id_ in keys:
        # For each string, we need size and file offset.  Each string is NUL
        # terminated; the NUL does not count into the size.
        offsets.append((len(ids), len(id_), len(strs), len(messages[id_])))
        ids += id_ + '\0'
        strs += messages[id_] + '\0'
    output = ''
    # The header is 7 32-bit unsigned integers.  We don't use hash tables, so
    # the keys start right after the index tables.
    # translated string.
    keystart = 7 * 4 + 16 * len(keys)
    # and the values start after the keys
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    # The string table first has the list of keys, then the list of values.
    # Each entry has first the size of the string, then the file offset.
    for offset1, line1, offset2, line2 in offsets:
        koffsets += [line1, offset1 + keystart]
        voffsets += [line2, offset2 + valuestart]
    offsets = koffsets + voffsets
    output = struct.pack("Iiiiiii",
                         0x950412deL,           # Magic
                         0,                     # Version
                         len(keys),             # # of entries
                         7 * 4,                 # start of key index
                         7 * 4 + len(keys) * 8, # start of value index
                         0, 0)                  # size and offset of hash table
    output += array.array("i", offsets).tostring()
    output += ids
    output += strs
    return output


def compile_catalog(path):
    """Builds a binary catalog for a given path to a gettext catalog"""

    ID = 1
    STR = 2

    outpath = os.path.splitext(path)[0] + '.mo'

    infile = open(path)
    try:
        lines = infile.readlines()
    finally:
        infile.close()

    messages = {}
    section = None
    fuzzy = False
    lno = 0
    msgid = msgstr = ''

    # Parse the catalog
    for line in lines:
        lno += 1
        # If we get a comment line after a msgstr, this is a new entry
        if line[0] == '#' and section == STR:
            _add(messages, msgid, msgstr, fuzzy)
            section = None
            fuzzy = False
        # Record a fuzzy mark
        if line[:2] == '#,' and 'fuzzy' in line:
            fuzzy = True
        # Skip comments
        if line[0] == '#':
            continue
        # Now we are in a msgid section, output previous section
        if line.startswith('msgid'):
            if section == STR:
                _add(msgid, msgstr, fuzzy)
            section = ID
            line = line[5:]
            msgid = msgstr = ''
        # Now we are in a msgstr section
        elif line.startswith('msgstr'):
            section = STR
            line = line[6:]
        # Skip empty lines
        line = line.strip()
        if not line:
            continue
        # XXX: Does this always follow Python escape semantics?
        line = eval(line)
        if section == ID:
            msgid += line
        elif section == STR:
            msgstr += line
        else:
            raise ValueError('Syntax error on %s:%d' % (path, lno))
    # Add last entry
    if section == STR:
        _add(messages, msgid, msgstr, fuzzy)

    # Compute output
    output = _generate(messages)

    outfile = open(outpath, 'wb')
    try:
        outfile.write(output)
    finally:
        outfile.close()
