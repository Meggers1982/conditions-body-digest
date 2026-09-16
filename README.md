# Conditions & Body Research Digest

A GitHub Actions workflow that searches curated journals in cancer, mental health, dermatology, allergy & immunology, and women's reproductive health on PubMed, filters out widely covered stories, runs a single Claude pass to write and pitch each study, and publishes results to a GitHub Pages dashboard.

---

## How it works

1. **PubMed search** — Queries journals by ISSN for studies published in the past 7 days
2. **Title screening** — Prioritises studies with signals of novelty (first-in-class, counterintuitive, overturns prior research). Excludes animal-only studies.
3. **SERPAPI media filter** — Checks Google News and skips any study with 3+ news results
4. **Abstract fetch** — Retrieves full abstracts for shortlisted studies
5. **Claude pass** — Writes structured JSON entries: headline, summary, why it matters, caveats, fact-check note, and pitch angles per publication type
6. **Artifact upload** — Saves JSON results as a GitHub Actions artifact
7. **Deploy job** — Downloads all job artifacts, merges and deduplicates by PMID, commits `data/results.json`, serves via GitHub Pages

---

## Dashboard

Features:
- Card view per study with headline, summary, caveats, fact-check notes
- Expandable pitch angles section showing one block per target publication type
- Filter by category, groundbreaking type, status, and date range
- Search across all study text and pitches
- Status tracking (New / Saved / Pitched / Passed) saved to localStorage
- Deduplication across runs — same PMID won't appear twice
- Relevance score (1–10) tuned for women's lifestyle journalism

---

## Schedule

Runs automatically every **morning at 7:00 AM ET**. All jobs run in parallel; the deploy job merges results and publishes the dashboard once all jobs complete.

Can also be triggered manually via **Actions → Conditions & Body Research Digest → Run workflow**.

---

## Categories

| Category | Journals | Jobs |
|---|---|---|
| Brain & Mental Health | 424 | 3 (chunks 1–3) |
| Cancer & Oncology | 169 | 2 (chunks 1–2) |
| Allergy & Immunology | 136 | 2 (chunks 1–2) |
| Womens Health & Reproduction | 102 | 1 |
| Dermatology | 51 | 1 |

Large categories are split into chunks so each job processes a manageable number of journals, keeping run times under 20 minutes.

---

## Journal list audit (2026-09-14)

**Method** — Pulled OpenAlex's top sources for this digest's subject areas over the prior year, diffed them against the CSVs (by any ISSN or title), and kept only titles NCBI lists with PubMed articles in the last 12 months. Because every row's journal enters the digest in full (no topic filter), a title was added only if its whole output fits the beat and isn't a mega-journal that would crowd the 30 candidate slots.

**Added (15)**

| Category | Journals |
|---|---|
| Cancer & Oncology | ESMO Open; The Breast; npj Breast Cancer; Cancer Epidemiology; Cancer Causes & Control |
| Womens Health & Reproduction | Journal of Assisted Reproduction and Genetics; Reproductive Biology and Endocrinology; Gynecological Endocrinology; International Journal of Women's Health |
| Dermatology | JAAD International; International Journal of Women's Dermatology; Clinical, Cosmetic and Investigational Dermatology |
| Brain & Mental Health | Cephalalgia; The Journal of Headache and Pain (migraine skews heavily female) |
| Allergy & Immunology | Allergy, Asthma & Clinical Immunology |

**Notable exclusions**
- **Volume** — Annals of Surgical Oncology (~2,550 PubMed articles/yr), Alzheimer's & Dementia (~1,070), Journal of Alzheimer's Disease (~1,090) would swamp the candidate slots.
- **Off-beat** — general neurology, dementia, Parkinson's/movement-disorder, and neurocritical/neurointerventional titles (mostly already carried by the mental-health and elderly-geriatric digests); surgical oncology (European Journal of Surgical Oncology); Innovation in Aging, Pancreatology, Toxicon, International Journal of Colorectal Disease.
- **Low pitchability** — Placenta (mostly basic science), npj Precision Oncology and Immuno-Oncology Technology (molecular/technical), Sexual Medicine (much of it male sexual dysfunction), npj Schizophrenia, Journal of ECT.
- **Case reports / regional** — Case Reports in Neurology; Polish, Indian, Japanese and Korean national titles.
- **Not in PubMed** — the largest OpenAlex hits in this area aren't PubMed-indexed and could never be searched: International Journal of Clinical Obstetrics and Gynaecology (~495 topic articles/yr), International Journal of Reproduction, Contraception, Obstetrics and Gynecology (~367), Annales de Dermatologie et de Vénéréologie – FMC, EJC Skin Cancer, Revue française d'allergologie.
- Journal of Assisted Reproduction and Genetics was flagged as "0 PubMed articles" by the candidate pipeline (a stale ISSN mixup); a direct PubMed check found ~418 articles/yr, so it was added.
- **Held back to keep additions modest** — Frontiers in Allergy, Allergologia et Immunopathologia, Dermatology and Therapy, Headache, F&S Reports.

The CSVs in `data/` are now hand-maintained: the source workbook (`~/PubMed_Journals_Categorized.xlsx`) no longer exists, so `scripts/extract_journals.py` has been deleted.

---

## Manual trigger

Go to **Actions → Conditions & Body Research Digest → Run workflow**.

- Leave **category** blank to run all jobs
- Enter an exact category name (e.g. `Dermatology`) to run just that category

---

## GitHub Pages setup

1. Go to **Settings → Pages**
2. Set source to **Deploy from a branch**
3. Branch: `main`, folder: `/ (root)`
4. Save — GitHub will serve `index.html` at the dashboard URL

---

## Required secrets

Add these in **Settings → Secrets and variables → Actions**:

| Secret | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key (`sk-ant-...`) |
| `SERPAPI_API_KEY` | SerpAPI key for Google News filtering |
| `SUPABASE_URL` | Supabase project URL (enables personalization from dashboard save/delete feedback) |
| `SUPABASE_KEY` | Supabase API key (read-only use; optional) |
| `DASHBOARD_REPO_TOKEN` | Token with push access to the shared `research-digest-dashboard` repo |

---

## Repo structure

```
.github/
  workflows/
    conditions-body-digest.yml   # GitHub Actions workflow (matrix + deploy)
scripts/
  conditions_body_digest.py      # Main pipeline: PubMed → Claude → JSON artifact
  merge_results.py               # Deploy job: merges artifacts → data/results.json
data/
  Cancer & Oncology.csv
  Brain & Mental Health.csv
  Dermatology.csv
  Allergy & Immunology.csv
  Womens Health & Reproduction.csv
  results.json                   # Auto-generated by deploy job; read by dashboard
index.html                       # GitHub Pages dashboard
requirements.txt
```

---

## Dashboard study card fields

Each study card on the dashboard shows:

- **Headline** — plain-language present-tense summary
- **Category & journal** — source metadata
- **Groundbreaking type** — Counterintuitive / Overturns prior research / First-in-class / Relevant women's health finding
- **Media coverage** — SERPAPI verification status
- **Relevance score** — 1–10, tuned for women's lifestyle journalism
- **The study** — what was done, who participated, key finding
- **Why it matters** — real-world significance for women specifically
- **Caveats** — limitations flagged automatically
- **Fact-check note** — corrections made during the Claude pass
- **Pitch angles** — one expandable block per target publication type (Women's Health Magazine, Health.com, Allure, Verywell Health, Everyday Health, Good Housekeeping, Cancer Today)
- **Status** — New / Saved / Pitched / Passed (tracked in your browser)
