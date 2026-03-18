# AI Model Coverage Strategy — Aggregate vs. Per-Model

> **Question:** When adding ChatGPT and Perplexity alongside Gemini, should brand performance metrics be shown per-model or aggregated?
>
> **Short answer:** Aggregate as the primary view, with model breakdown as a drill-down.

---

## The Right Mental Model: Think Like SEO

In traditional SEO, you track **overall organic traffic and rankings** — you don't force your marketing team to think "our Google rank vs. our Bing rank vs. our DuckDuckGo rank" as separate KPIs. But you absolutely care if you're completely missing from one major engine.

AI search works the same way. The marketing team's question is: **"Are we visible when people use AI to search?"** — not "are we visible specifically in Gemini?"

---

## Why Aggregation Works as the Primary View

**1. The optimization actions are identical regardless of model.**
Whether your visibility dropped in ChatGPT or Perplexity, the fix is the same: get cited by authoritative sources, create content that AI models reference, improve your brand's authority signals. A per-model view doesn't change what you do.

**2. Marketers report upward, not laterally.**
Your CMO wants one number — *"our AI search awareness score is 6.8, up from 6.2 last month."* Showing three separate scores per model adds cognitive load without adding decision-making value.

**3. Aggregation produces stronger statistical signals.**
With more data points (3 models × N queries instead of 1 model × N queries), your visibility trends and anomaly detection become more reliable. A single-model score is noisier. Aggregated is more trustworthy.

**4. Users don't know or care which model powers their tool.**
Most people using AI search don't know if they're on ChatGPT, Copilot, or Gemini. From a brand exposure standpoint, the audience is "people using AI" — not "Gemini users specifically."

---

## Where Per-Model View Still Matters

There are two scenarios where model-level data is genuinely useful:

**Scenario 1: You're invisible in one major model.**
If your brand scores 8/10 in Gemini but 2/10 in ChatGPT, that's a critical gap — ChatGPT has the largest user base. This should surface as an **alert or callout**, not as a primary dashboard view.

**Scenario 2: Different models serve different audiences.**
Perplexity skews heavily technical/developer. ChatGPT is mainstream consumers. Gemini is Google-ecosystem users. If a brand sells developer tools, their Perplexity score matters more than their ChatGPT score. Advanced users might want to weight or filter by model.

---

## Recommended Architecture

### Primary Layer — What Marketing Teams See Daily
- Aggregated awareness score (weighted average across all models)
- Aggregated visibility rate, ranking, sentiment
- All existing charts and competitive analysis — pulling from all models combined

### Secondary Layer — Model Coverage Indicator
A simple status row, not a full separate dashboard:

```
AI Model Coverage
ChatGPT     ████████░░  78% visibility
Gemini      ██████████  94% visibility
Perplexity  ████░░░░░░  41% visibility  ⚠ Gap detected
```

This surfaces "you're missing from Perplexity" without restructuring the entire product.

### Tertiary Layer — Model Filter for Power Users
A simple dropdown alongside existing time range and segment filters on all dashboards. Most users will never touch it. The ones who do are your most engaged customers.

---

## How to Weight the Aggregation

Don't treat all models equally — weight by estimated market share so the aggregate score reflects actual user exposure:

| Model | Estimated Weight |
|---|---|
| ChatGPT | ~55% |
| Gemini | ~25% |
| Perplexity | ~15% |
| Others (Copilot, Claude, etc.) | ~5% |

You can also allow users to customize weights if their target audience skews toward a specific platform.

---

## Bottom Line

| View | Purpose | Who Uses It |
|---|---|---|
| **Aggregated metrics** | Primary dashboard — unified AI search presence | All users, daily |
| **Model coverage indicator** | Callout for gaps across models | All users, as needed |
| **Model filter** | Drill-down for per-model analysis | Power users |

Aggregate everything into unified metrics — that's what your marketing team will use and report on. Forcing per-model views as primary would make the product feel like a developer tool, not a marketing tool.

> The brands paying you don't care *which* AI recommended them — they care *whether* AI recommends them.
