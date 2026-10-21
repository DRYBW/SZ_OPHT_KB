# MANIFEST scope note — V3 stage axis (card t_aa1b7f12)

# covered files: 44

# Excluded from the hash list, with the reason:
#   MANIFEST.sha256                a record cannot contain its own hash
#   logs/*.log                     rewritten by any re-run; hashing them would fail the
#                                  check for reasons unrelated to the delivered artefacts
#   out/GATE_READOUT.md            rewritten by the gate/verification step (the one command
#   out/GATE_READOUT.json          a reviewer is expected to re-run)
#   out/STAGE_LITERAL_SURFACE.tsv  same reason
#
# sha256 of the excluded derived files at delivery time:
#   out/GATE_READOUT.json  f86321027be7e76287e95061f731a22e5fab30dfb0a5dfbce067a45046572db3
#   out/GATE_READOUT.md  48d7c4f5dfa83af05196f0d821c2299c913db11a6194e50507e90903edf2eead
#   out/STAGE_LITERAL_SURFACE.tsv  864537a62a0429d54120195e66c36eab966ea3376059608f690b437fe25ae4dd
#
# Verification:  cd <this directory> && sha256sum -c MANIFEST.sha256
# Expected: every line 'OK', exit code 0.
