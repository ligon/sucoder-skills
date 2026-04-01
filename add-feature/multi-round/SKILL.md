---
name: multi-round
description: Use this skill to add features to LSMS-ISA countries with post-planting/post-harvest (pp/ph) dual-round survey structure. This skill should be used when a user wants to add or fix a feature in Nigeria, Ethiopia, Tanzania (2008-15), or other countries where a single wave directory contains data from two survey rounds. Covers distinct t-value assignment, attrition deduplication, the !make requirement, and duplicate-index bug avoidance.
---

# Multi-Round (PP/PH) Feature Implementation

This skill provides guidance for adding features to LSMS-ISA countries that collect data in two rounds per wave: post-planting (pp) and post-harvest (ph). This is a sub-skill of `add-feature` and assumes familiarity with the general add-feature workflow.

## When to use this skill

Use this skill when the target country has **two source files per wave directory** representing different survey rounds (planting and harvest visits). The YAML path cannot express this --- a Python script with `materialize: make` is always required.

## Identifying pp/ph countries

### File naming patterns

| Country | Program | Pattern | Example |
|---------|---------|---------|---------|
| Nigeria | GHS/LSMS-ISA | `sect*_plantingw*.dta` / `sect*_harvestw*.dta` | `sect1_plantingw4.dta`, `sect1_harvestw4.dta` |
| Ethiopia | ESS | `sect*_pp_w*.dta` / `sect*_ph_w*.dta` | `sect1_pp_w4.dta`, `sect1_ph_w4.dta` |
| Tanzania | NPS (2008-15 only) | Single file with `round` column | `HH_SEC_B.dta` contains rounds 1--4 |

To confirm whether a country has pp/ph structure, inspect the `Data/` directory for a wave:

```bash
ls lsms_library/countries/{Country}/{wave}/Data/ | grep -iE 'plant|harvest|_pp_|_ph_'
```

If files appear in pairs (one planting, one harvest), the wave has dual-round structure.

### Which features are affected

**Every feature that draws from both rounds** needs a script. Common affected features:
- `household_roster` --- people present at planting vs harvest (attrition between rounds)
- `food_acquired` --- food consumption recorded separately in each round
- `household_characteristics` --- household-level attributes from both rounds
- `assets` --- durable goods inventories
- `shocks` --- may be asked in only one round (check the questionnaire)

Some features may only use data from a single round (e.g., shocks asked only at harvest). These can sometimes use the YAML path if they reference only one file. Verify by checking which source file contains the needed variables.

## Why YAML cannot express this

The `data_info.yml` YAML path assumes:
1. One directory = one `t` value
2. One source file per feature per wave
3. No per-row `t` assignment needed

In pp/ph countries, a single wave directory (e.g., `Nigeria/2018-19/`) contains two source files that need **different `t` values**. The YAML path has no mechanism to load two files, assign different `t` values, and concatenate. Therefore, pp/ph features **must** use `materialize: make` (or `!make`) in `data_scheme.yml`.

## Index construction: distinct `t` values per round

The core requirement: each round must receive a **distinct `t` value** so the same household does not create duplicate index entries.

### Standard `t` value conventions

- **Nigeria**: Quarter-based --- `2018Q3` (post-planting, ~Sep-Oct), `2019Q1` (post-harvest, ~Jan-Mar)
- **Ethiopia**: Some features use a single wave label (e.g., `2018-19`) when only one round's data is used. When both rounds are included, distinct `t` values are needed.
- **Tanzania `2008-15/`**: Wave labels mapped from the `round` column --- `2008-09`, `2010-11`, `2012-13`, `2014-15`

### Assigning `t` in scripts

Use a lambda in `idxvars` to assign a constant `t` value to every row from a given file:

```python
# Post-planting
idxvars_pp = dict(
    i='hhid',
    t=('hhid', lambda x: '2018Q3'),   # constant t for all pp rows
    v='ea',
    pid='indiv',
)
pp = df_data_grabber('../Data/sect1_plantingw4.dta', idxvars_pp, **myvars_pp)

# Post-harvest
idxvars_ph = dict(
    i='hhid',
    t=('hhid', lambda x: '2019Q1'),   # different t for all ph rows
    v='ea',
    pid='indiv',
)
ph = df_data_grabber('../Data/sect1_harvestw4.dta', idxvars_ph, **myvars_ph)
```

## The duplicate-index bug

This is the single most common bug when working with pp/ph countries. It causes 50--87% duplicate indices and roughly doubles the expected household count.

### How it happens

```python
# BUG: Both rounds get the same t value
pp['t'] = '2018-19'
ph['t'] = '2018-19'
df = pd.concat([pp, ph])
# Household 12345 now appears twice with identical (t, i) index
```

### How to detect it

```python
dup_rate = df.index.duplicated().mean()
print(f"Duplicate rate: {dup_rate:.1%}")
# If > 10%, almost certainly a pp/ph t-value collision
```

Or use the built-in diagnostics:

```python
from lsms_library.diagnostics import is_this_feature_sane
report = is_this_feature_sane(df, country='Nigeria', feature='household_roster')
report.summarize()
# Will flag high duplicate rate
```

### How to fix it

Assign distinct `t` values to each round (see "Assigning `t` in scripts" above). If the feature has already been built incorrectly, the fix is always in the wave-level `.py` script.

## Deduplication: attrition between rounds

Households and individuals may appear in one round but not the other. Common reasons:
- A household member left, died, or was born between planting and harvest
- A household was not reachable during one round
- The household split between rounds

### Standard deduplication pattern

After concatenating pp and ph DataFrames, remove rows where an individual appeared in one round but has no actual data:

```python
df = pd.concat([pp, ph])

# Drop rows where all value columns are missing (person left between rounds)
df = df.replace('', pd.NA).sort_index().dropna(how='all')
```

For person-level tables (`household_roster`), `dropna(how='all')` removes individuals who were enumerated in the planting round but had left by harvest (or vice versa) --- their row in the other round will have all-NaN values.

For item-level tables (`food_acquired`), no special deduplication is needed beyond distinct `t` values, because each round's items are independent observations.

## Variable name differences between rounds

Source variable names often differ between pp and ph files within the same wave. Always check both files:

```python
import pyreadstat
_, meta_pp = pyreadstat.read_dta('../Data/sect1_plantingw4.dta', metadataonly=True)
_, meta_ph = pyreadstat.read_dta('../Data/sect1_harvestw4.dta', metadataonly=True)
print("PP columns:", meta_pp.column_names)
print("PH columns:", meta_ph.column_names)
```

Example from Nigeria 2018-19 `household_roster`:
- Age variable: `s1q6` (planting) vs `s1q4` (harvest)
- Same concept, different variable name

Define separate `myvars` dicts for each round when variable names differ.

## Script template

Complete template for a pp/ph feature script:

```python
#!/usr/bin/env python
"""Extract {feature_name} for {Country} {wave}.

Source files:
  - {pp_file}  (post-planting, {pp_t})
  - {ph_file}  (post-harvest, {ph_t})
"""
import sys
import pandas as pd

sys.path.append('../../../_/')
from lsms_library.local_tools import df_data_grabber, to_parquet

# --- Post-planting ---
idxvars_pp = dict(
    i='hhid',
    t=('hhid', lambda x: '{pp_t}'),
    v='ea',
    # pid='indiv',  # if person-level
)
myvars_pp = dict(
    # Column mappings for planting file
)
pp = df_data_grabber('../Data/{pp_file}', idxvars_pp, **myvars_pp)

# --- Post-harvest ---
idxvars_ph = dict(
    i='hhid',
    t=('hhid', lambda x: '{ph_t}'),
    v='ea',
    # pid='indiv',  # if person-level
)
myvars_ph = dict(
    # Column mappings for harvest file (may differ from pp)
)
ph = df_data_grabber('../Data/{ph_file}', idxvars_ph, **myvars_ph)

# --- Combine ---
df = pd.concat([pp, ph])
df = df.replace('', pd.NA).sort_index().dropna(how='all')

to_parquet(df, '{feature_name}.parquet')
```

## data_scheme.yml configuration

Features using this pattern must be marked with `materialize: make` in `data_scheme.yml`:

```yaml
Data Scheme:
  household_roster:
    index: (t, v, i, pid)
    Sex: str
    Age: int
    Generation: int
    Distance: int
    Affinity: str
    materialize: make
```

The `!make` shorthand is also accepted for legacy features that predate the schema definition:

```yaml
  food_acquired: !make
```

## wave_folder_map interaction

Some pp/ph countries also use `wave_folder_map` (see the multi-round-waves local skill). Tanzania's `2008-15/` directory is both a multi-round folder (4 waves in one directory) and uses a `round` column rather than separate pp/ph files. These are distinct mechanisms:

- **pp/ph** = two source files per wave, each needing a different `t` → solved by script-level `t` assignment
- **wave_folder_map** = multiple logical waves sharing one physical directory → solved by `Wave(year=..., wave_folder=...)` and filtering by `t`

Both require `materialize: make`. A single script may handle both patterns (e.g., Tanzania `2008-15/_/food_acquired.py`).

## Reference implementations

### Nigeria (canonical pp/ph pattern)

- **`Nigeria/2018-19/_/household_roster.py`** --- The clearest example: loads `sect1_plantingw4.dta` (t=`2018Q3`) and `sect1_harvestw4.dta` (t=`2019Q1`), concatenates, drops attrited individuals.
- **`Nigeria/2018-19/_/food_acquired.py`** --- PP/PH with food item and unit label harmonization via `categorical_mapping.org`. Uses a shared `extract_food()` helper called once per round.

### Ethiopia (ESS pattern)

- **`Ethiopia/2018-19/_/food_acquired.py`** --- Delegates to a shared `ethiopia.food_acquired()` function. Some features use only one round's data (e.g., shocks from `sect9_hh_w4.dta` only).
- **`Ethiopia/2018-19/_/shocks.py`** --- Example of a feature that uses only one round (no pp/ph splitting needed), but the country still has the dual-round structure for other features.

### Tanzania (multi-round single file)

- **`Tanzania/2008-15/_/`** --- Single `.dta` file with a `round` column. Script reads the column, maps values to wave labels, and filters. Different from the two-file pp/ph pattern but uses the same `materialize: make` mechanism.

## Common bugs and how to avoid them

| Bug | Cause | Fix |
|-----|-------|-----|
| 50--87% duplicate indices | Both rounds assigned the same `t` value | Assign distinct `t` values (e.g., `2018Q3` / `2019Q1`) |
| Missing half the data | Only loaded pp or ph, not both | Load both files and concatenate |
| Wrong variable names | Used pp variable names for ph file (or vice versa) | Check column names in both files separately |
| Ghost rows after concat | Individual enumerated in pp but absent in ph | `dropna(how='all')` after concat |
| Double-counted households | Concatenated without distinct `t` but feature is household-level | Assign distinct `t` values; for hh-level features, also check if data is truly from both rounds or just one |
| `data_info.yml` used for pp/ph feature | YAML cannot express two-file + distinct-`t` pattern | Switch to `materialize: make` with a `.py` script |

## Checklist for adding a pp/ph feature

1. Confirm the country has dual-round structure (check file naming in `Data/`)
2. Identify which source files contain the needed variables for each round
3. Check variable names in **both** pp and ph files (they may differ)
4. Write a `.py` script that:
   - Loads pp file with distinct `t` value
   - Loads ph file with different `t` value
   - Concatenates and deduplicates
   - Uses `get_dataframe()` or `df_data_grabber()` for data access
   - Uses `to_parquet()` for output
5. Mark the feature as `materialize: make` in `data_scheme.yml`
6. Verify with `is_this_feature_sane()` --- check duplicate rate is reasonable
7. Confirm both rounds appear in `df.index.get_level_values('t').unique()`

## Relationship to the add-feature parent skill

This skill extends the general `add-feature` workflow (Steps 5--6 specifically). When the target country is identified as a pp/ph country:

- **Step 5** (Decide YAML vs Script): The answer is always **script** for features that use both rounds' data.
- **Step 6** (Write the configuration): Use the script template from this skill. The `data_scheme.yml` entry must include `materialize: make`.
- **Step 7** (Verify): Pay special attention to duplicate rates and `t` value coverage in diagnostics.

All other steps in the `add-feature` workflow (schema definition, variable mapping, verification, consolidation review) apply unchanged.
