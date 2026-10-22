# Regression-harness report -- self-test fixture (no-op change)

Declared change: nothing at all

Before arm: `{"env": {"EYEKB_TISSUE_SCOPE": "1"}}`
After arm:  `{"env": {"EYEKB_TISSUE_SCOPE": "1"}}`

Recorded set: 721 clusters / 1495330 cells / 28 volumes

## Ruling: **PASS**

a change may not be reported as complete while any dataset's cell-weighted consistent share has fallen, unless the drop is attributed to a named cluster + named cause + named row/panel

## Overall, cell-weighted

| grade | before % | after % | delta pp | clusters before | clusters after |
|---|---:|---:|---:|---:|---:|
| consistent | 40.852 | 40.852 | +0.000 | 290 | 290 |
| related | 16.936 | 16.936 | +0.000 | 88 | 88 |
| inconsistent | 20.108 | 20.108 | +0.000 | 173 | 173 |
| mixed | 22.104 | 22.104 | +0.000 | 170 | 170 |

## Per dataset

| dataset | clusters | cells | before consistent % | after consistent % | delta pp |
|---|---:|---:|---:|---:|---:|
| CX01_retina_snRNA | 37 | 97015 | 70.11 | 70.11 | +0.000 |
| CX02_adult_retina | 48 | 85452 | 72.376 | 72.376 | +0.000 |
| CX03_retina_multiome | 31 | 51591 | 36.842 | 36.842 | +0.000 |
| CX04_cowan_fovea | 25 | 19753 | 67.772 | 67.772 | +0.000 |
| CX04_cowan_organoid | 15 | 43847 | 90.134 | 90.134 | +0.000 |
| CX04_cowan_periphery | 33 | 34702 | 54.239 | 54.239 | +0.000 |
| CX07_iPSC_organoid_POAG | 21 | 46275 | 6.788 | 6.788 | +0.000 |
| CX08_RPE_choroid_scRNA | 20 | 73513 | 36.63 | 36.63 | +0.000 |
| CX08_RPE_choroid_snRNA | 18 | 70474 | 31.834 | 31.834 | +0.000 |
| CX09_voigt_RPE_choroid | 16 | 3624 | 74.31 | 74.31 | +0.000 |
| CX10_hiPSC_RPE | 25 | 54894 | 11.475 | 11.475 | +0.000 |
| CX11_posterior_eye_atlas | 20 | 54697 | 21.16 | 21.16 | +0.000 |
| CX12_ocular_surface_snRNA | 21 | 37264 | 35.997 | 35.997 | +0.000 |
| CX13_TM_corneal_scleral | 29 | 51414 | 38.999 | 38.999 | +0.000 |
| CX13_central_cornea | 16 | 35890 | 6.629 | 6.629 | +0.000 |
| CX13_ciliary_body | 17 | 32282 | 21.495 | 21.495 | +0.000 |
| CX13_iris | 17 | 55990 | 18.646 | 18.646 | +0.000 |
| CX13_lens | 11 | 13538 | 0.0 | 0.0 | +0.000 |
| CX14_TM_ciliary_snRNA | 17 | 78110 | 34.716 | 34.716 | +0.000 |
| CX15_optic_nerve_all | 46 | 71997 | 41.873 | 41.873 | +0.000 |
| CX16_tabula_sapiens_eye | 36 | 31808 | 18.052 | 18.052 | +0.000 |
| CX17_mouse_retina_all | 36 | 71751 | 0.0 | 0.0 | +0.000 |
| PRE_GSE199013 | 38 | 42473 | 36.859 | 36.859 | +0.000 |
| PRE_GSE268630 | 36 | 59276 | 71.705 | 71.705 | +0.000 |
| PRE_OA-D001 | 32 | 62649 | 74.97 | 74.97 | +0.000 |
| PRE_OA-D002 | 19 | 69411 | 35.879 | 35.879 | +0.000 |
| PRE_OA-D004 | 21 | 81867 | 44.765 | 44.765 | +0.000 |
| PRE_OA-D068 | 20 | 63773 | 53.785 | 53.785 | +0.000 |

## Cells moved, by grade transition

| transition | clusters | cells |
|---|---:|---:|

## Clusters whose ranking moved (0 clusters / 0 cells)

| volume | cluster | n_cells | tissue | before | after | grade |
|---|---|---:|---|---|---|---|

## Harness pre-image

```json
{
 "role": "the harness's own pre-image: every number it reports is re-derivable from these files plus the frozen inputs",
 "files": [
  {
   "path": "scripts/n3_harness.py",
   "sha256": "9f55a8ccbd20219615b660218ac2ac7ba8602242ea62c51bb98adcec0bedb807",
   "bytes": 15673
  },
  {
   "path": "scripts/wave_common.py",
   "sha256": "f8226dc4aefc799ace536b66748ece67494826031c21242b6e25b44389f37863",
   "bytes": 18547
  }
 ],
 "inputs": {
  "input_manifest_sha256": "d2f1211613f0bbd6da6b5a21c179b8cadd0a9bca5678bfa524b56c619348dc61",
  "recordings_sha256": {
   "annotation_evidence_report.json": "325b0592893cb90a739f464ed560b05bd2cd395ccee1a46fe72df036447aa18c"
  },
  "fixed_sha256": {
   "ledger_cluster_level.tsv": "9e2a0844ad639e0ba0ed6cccfa3ca7f109cde98d4f91568621cd0e4df85b1427",
   "kb_family_crosswalk_v2.json": "c704b3a5dc5d5dbf024b6cb101356a4c23eacd9978bba0393c07e81d550e64f8",
   "_tissue_class_crosswalk_v1.json": "a06a753af39700541962bf5dc03472635e024130b3f297d57bc1ac2802a5682d",
   "markers_cl_alignment_v2_unified.json": "48051cdae915b82e6e7812da9b98f93b41f51c5fac14bdb370bd5ccdb969a0a1",
   "cl-base.obo": "c6274fb65cdf740b983a06b74cb678814249d7f8e580c2ec9de54bf204a2b1c7",
   "markers_v10_antseg_increment.json": "c488fc26b615e57addd1d0828b20293d07fb3a7a92baedca5d32a528bc597f47",
   "eyekb_core.py": "3dadbbbaf2631da0f48760beb95278f5fabd675e6108282c9080fae67a61d736",
   "markers_membrane_v1.json": "c4268a6e0655f6d89f913289766f3edc062f116a82a983abbfccd7cee54198d1",
   "markers_k9_ocs_increment.json": "139b622082f80a6c3962b7a2532dc8c3fed8a87a92154ccd98491ef4f2540a71",
   "markers_v12_holefill_increment.json": "a9bb4feb86e61360215a403baef74f8eb661fad5d7158de32940c54f52a8475f",
   "probe_tool_panel_identity.py": "bcf619b252a248bd64de00c3d61cd64d4c39dde9dff864d8b3694ed2de666370",
   "probe_opticnerve_scope_ab.py": "f84301d6c41c366a1402a00c90e319a06d99982f8b5684573ed703bdeaa0f500",
   "FINDING_OPTIC_NERVE_REGRESSION_20261022.md": "92ea5d44c7a97925bdad54c586da5dd23ec0e7cd31c1f27e5502290d5cbe0311",
   "GATE_A3.json": "5b77be8f1cc2a657e08ce022d6ca1e2e76062f11b22930603deffd9adab027dc",
   "gate_a3_no_collateral.py": "e3e1c6c279a65c63acb72c4558fb5b9dc30871d99f7e55575aaca4fe9bdb94d4",
   "REPORT_TISSUE_SCOPE_v2.0_DEFAULT_ON.md": "a7d5f157f3e8355c12cd2e01e3c310e84ded7d1e9b855d6538d4791813812f88",
   "PREREG_TISSUE_SCOPE_20261020.md": "1b8983ac117da4a275e91ee8bfc86b56e7889af97aa3eefd9a49984a3f3f339c",
   "cross_dataset_summary.csv": "2f90ca79ec1abd14698ebc9dd06659f45013bdca1e5e475b637da1d9f0160e81",
   "EyeKB更新后重评_20261021.md": "069bd08f5dedb076ed649449d031ab8f5ee939611bb18d604c1a29a4dedf00cf"
  }
 }
}
```
