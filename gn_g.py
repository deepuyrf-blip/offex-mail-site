import os
# The Switch/History section is generated directly by gn_e.py now, and the
# strings (history/history_empty) plus the foreground-service manifest entries
# are emitted by gn_h.py and gn_o.py. This step is intentionally a no-op kept
# for pipeline compatibility.
print("G: no-op (layout/strings/manifest handled by gn_e, gn_h, gn_o)")
