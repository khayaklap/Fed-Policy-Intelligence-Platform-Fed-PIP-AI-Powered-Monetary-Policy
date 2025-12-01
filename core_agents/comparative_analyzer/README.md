# Comparative Analyzer - Fed Policy Episode Comparison & Pattern Analysis

**Compare Fed policy episodes, identify recurring patterns, and extract lessons from history.**

The Comparative Analyzer is the fourth core agent in the Fed Policy Intelligence Platform. It provides powerful tools for understanding current Fed policy by comparing it to similar historical episodes.

---

## 🎯 Quick Start

```python
from comparative_analyzer_tools import compare_episodes_tool

# Compare two episodes
result = compare_episodes_tool(
    'gfc_response_2007_2008',
    'covid_response_2020'
)
print(f"Similarity: {result['overall_similarity']:.3f}")
```

## 📦 Installation

```bash
pip install -r comparative_analyzer_requirements.txt
```

## 🛠️ Five ADK Tools

1. **compare_episodes_tool** - Compare two episodes across 6 dimensions
2. **identify_pattern_tool** - Identify which pattern current policy matches  
3. **find_similar_episodes_tool** - Rank episodes by similarity
4. **compare_fed_chairs_tool** - Compare Fed chairs' approaches
5. **extract_lessons_tool** - Extract lessons from multiple episodes

## 📊 13 Available Episodes (1979-2024)

- volcker_disinflation_1979_1982
- greenspan_1987_crisis
- dotcom_tightening_1999_2000
- gfc_response_2007_2008
- covid_response_2020
- inflation_fight_2022_2023
- ...and 7 more

## 🎭 6 Pattern Types

- v_shaped_response - Rapid cuts then hikes
- gradual_tightening - Slow steady increases
- emergency_easing - Fast crisis cuts
- extended_pause - Long unchanged
- pivot - Sharp reversal
- overshooting - Too far then reverse

## 📈 Key Insights

1. **Fed patterns do recur** - Same situations get same responses
2. **Context matters** - Similar policy → different outcomes
3. **Fed learns** - 2020 faster than 2008 (COVID vs GFC)
4. **Chairs differ** - Volcker vs Powell styles
5. **History guides** - But doesn't script

## 🧪 Testing

```bash
pytest test_comparative_analyzer.py -v
```

**Lines of Code:** ~3,600
**Tools:** 5
**Episodes:** 13
**Chairs:** 5

See full documentation in this file for detailed examples and API reference.
