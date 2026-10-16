# Do overseers catch wrong LLM grades?

A research plan and starter evaluation for measuring **scalable oversight from the reviewer's side**: when a capable model grades work and a human (or a weaker model) approves it, how often is that approval a rubber stamp?

**Status:** pilot design and tooling. **No experimental results yet.** Everything in `data/` is synthetic, and `simulate.py` exists only to test the pipeline.

Author: [Gul Sher Baloch, PhD](https://gulsherbaloch.com) · Background and motivation: [What 1,946 teacher-reviewed LLM gradings taught me about oversight](https://gulsherbaloch.com/oversight/)

---

## Why this question

I ran [GradexAI](https://gulsherbaloch.com/#work), an LLM exam-grading tool with teacher review of AI grades. Across 1,946 AI gradings, teachers approved **91.7%**. That number looked like success, but it cannot tell two situations apart:

1. the model was right about 91.7% of the time, and teachers caught its mistakes; or
2. the model was wrong more often, and teachers deferred to it.

We never planted known errors, so we never measured how many wrong grades were approved. The approval rate measured agreement, not oversight. Most published oversight results share this blind spot: they report the quality of the AI's output and rarely the **catch rate** of the reviewer.

## Research questions

- **RQ1. Catch rate.** When an LLM-assigned grade contains a known error, how often do reviewers flag it? How does this vary with error type (over-credit, under-credit, wrong rationale) and error size?
- **RQ2. Weak reviewers.** How do weaker models acting as reviewers compare with humans? This uses the weak-to-strong framing, with the weak reviewer standing in for humans overseeing stronger systems.
- **RQ3. Interventions.** Which of these raise catch rate without raising false flags much: showing the rubric next to the grade, adding a model-written critique, or showing a debate between two models over the grade?
- **RQ4. Deference.** Does a fluent, confident rationale lower catch rate even when the score is wrong?

## Design

1. **Items.** Short-answer questions with a rubric, a student answer and a verified correct score.
2. **Planted errors.** On a controlled fraction of items, change the AI's grade:
   - `over_credit`: score raised above the correct score
   - `under_credit`: score lowered below it
   - `rationale`: score unchanged, but the rationale claims a rubric point the answer misses
3. **Review.** Reviewers see question, rubric, answer, AI score and AI rationale, and choose *approve* or *flag*. The answer key stays hidden.
4. **Metrics.** Catch rate (recall on planted errors) with 95% Wilson intervals, false-flag rate on correct gradings, catch rate by error type, and the approval rate the product would have reported.
5. **Conditions.** Baseline vs. rubric shown vs. critique shown vs. debate shown, within subjects where possible.

The core output is the gap between **approval rate** (what dashboards show) and **catch rate** (what oversight actually achieves).

## Scope for a four-month fellowship

| Month | Work |
|---|---|
| 1 | Build an item bank from public, openly licensed short-answer data or synthetic items; verify correct scores; pilot error planting |
| 2 | Weak-model reviewers across several open and API models; establish baselines (RQ1, RQ2) |
| 3 | Intervention conditions (RQ3, RQ4); a small human-reviewer study if approved |
| 4 | Analysis, release of dataset and code, paper write-up |

Compute needs are modest: open models and public APIs, no training runs.

## Repository

```
oversight_eval/
  make_items.py   plant errors into graded items; writes review_set.jsonl and a hidden answer_key.jsonl
  score.py        score reviewer decisions against the key (catch rate, CI, false flags, by type)
  simulate.py     SIMULATION ONLY: synthetic reviewer decisions for testing the pipeline
data/
  example_items.jsonl   10 synthetic science items with rubrics and verified scores
```

Standard library only (Python 3.9+).

```bash
python -m oversight_eval.make_items data/example_items.jsonl out --error-rate 0.4 --seed 7
python -m oversight_eval.simulate out/answer_key.jsonl out/decisions.jsonl --catch 0.4 --false-flag 0.05
python -m oversight_eval.score out/answer_key.jsonl out/decisions.jsonl
```

To score real reviewers, replace `out/decisions.jsonl` with one line per decision:

```json
{"id": "q03", "reviewer": "reviewer_01", "decision": "flag"}
```

## Related work

- Bowman et al., *Measuring Progress on Scalable Oversight for Large Language Models* (2022)
- Burns et al., *Weak-to-Strong Generalization* (2023)
- Sharma et al., *Towards Understanding Sycophancy in Language Models* (2023)
- Anthropic, *Automated Alignment Researchers* (2026), where agents improved weak-to-strong supervision but also tried to game their setup
- My own work on learning under label noise: Hyder, Baloch et al., *A robust deep learning framework for mitigating label noise with dual selective attention*, IEEE Access (2025)

## Planned next steps

- [ ] Expand the item bank beyond the synthetic examples
- [ ] Add LLM-reviewer runners (open models and API models)
- [ ] Add intervention conditions (rubric, critique, debate)
- [ ] Pre-register metrics and analysis before running any study

## License

MIT
