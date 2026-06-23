from server.graphs import ib_lending
lod = "<<paste the real '2nd Line of Defense Assessment' section text>>"
print("matches:", bool(ib_lending._lod_label_re("Updated UBS Expected Case").search(lod)))
for line in lod.splitlines():
    if "Expected Case" in line and "Updated" in line:
        print("LINE   :", repr(line))
        print("CODEPTS:", [hex(ord(c)) for c in line[:45]])
        break
