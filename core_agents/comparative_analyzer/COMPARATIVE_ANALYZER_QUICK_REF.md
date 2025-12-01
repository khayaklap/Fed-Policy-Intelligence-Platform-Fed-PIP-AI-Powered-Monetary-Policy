# COMPARATIVE ANALYZER - QUICK REFERENCE

## 🚀 **Installation**
```bash
pip install -r comparative_analyzer_requirements.txt
```

## 🛠️ **Five Tools**

### **1. Compare Episodes**
```python
compare_episodes_tool('gfc_response_2007_2008', 'covid_response_2020')
# Returns: similarity (0-1), dimensions, similarities, differences, lessons
```

### **2. Identify Pattern**
```python
identify_pattern_tool(meetings, min_meetings=6)
# Returns: best pattern, confidence, features, interpretation
```

### **3. Find Similar**
```python
find_similar_episodes_tool('inflation_fight_2022_2023', top_n=5)
# Returns: ranked list of similar episodes
```

### **4. Compare Chairs**
```python
compare_fed_chairs_tool('ben_bernanke', 'jerome_powell')
# Returns: styles, episodes, achievements, interpretation
```

### **5. Extract Lessons**
```python
extract_lessons_tool(['gfc_response_2007_2008', 'covid_response_2020'])
# Returns: lessons by category, takeaways
```

## 📊 **13 Episodes** (1979-2024)

| Episode | Chair | Rate Change | Key Feature |
|---------|-------|-------------|-------------|
| volcker_disinflation_1979_1982 | Volcker | +1100bp to 20% | Broke inflation |
| greenspan_1987_crisis | Greenspan | -50bp | Black Monday |
| dotcom_tightening_1999_2000 | Greenspan | +175bp | 17 hikes |
| dotcom_bust_easing_2001 | Greenspan | -475bp | 9/11 response |
| housing_boom_2004_2006 | Greenspan/Bernanke | +425bp | 17 consecutive |
| gfc_response_2007_2008 | Bernanke | -500bp to 0% | QE introduced |
| gfc_recovery_2009_2015 | Bernanke/Yellen | 0% for 7 years | ZLB + QE1-3 |
| normalization_2015_2018 | Yellen/Powell | +225bp | Gradual liftoff |
| 2019_pivot | Powell | -75bp | Insurance cuts |
| covid_response_2020 | Powell | -150bp in 13 days | Fastest ever |
| covid_recovery_2020_2021 | Powell | 0% for 17 months | "Transitory" |
| inflation_fight_2022_2023 | Powell | +525bp | 4x 75bp hikes |
| higher_for_longer_2023_2024 | Powell | 5.5% for 15+ months | Restrictive |

## 🎭 **6 Patterns**

| Pattern | Description | Examples |
|---------|-------------|----------|
| v_shaped_response | Rapid cuts → rapid hikes | COVID 2020 |
| gradual_tightening | Slow steady increases | 2004-06, 2015-18 |
| emergency_easing | Fast crisis cuts | GFC, COVID |
| extended_pause | Long unchanged | 2009-15 ZLB |
| pivot | Sharp reversal | 2019, 2021-22 |
| overshooting | Too far → reverse | 2018 |

## 🪑 **5 Fed Chairs**

| Chair | Tenure | Style | Notable |
|-------|--------|-------|---------|
| Volcker | 1979-87 | Inflation hawk | 20% rates |
| Greenspan | 1987-06 | Data-dependent | "Fed put" |
| Bernanke | 2006-14 | Innovative | QE pioneer |
| Yellen | 2014-18 | Cautious | Labor-focused |
| Powell | 2018-now | Pragmatic | Fast responder |

## 📏 **6 Comparison Dimensions**

1. **Speed** - How fast Fed acted (bp/month)
2. **Magnitude** - Size of response (total bp)
3. **Duration** - Length of episode (months)
4. **Economic Context** - Similar conditions
5. **Policy Tools** - Conventional vs unconventional
6. **Outcome** - Results achieved

## 🎓 **5 Lesson Categories**

1. **Timing** - When to act
2. **Magnitude** - How much to move
3. **Communication** - How to signal
4. **Tools** - Which tools to use
5. **Mistakes** - What went wrong

## 🧪 **Testing**
```bash
pytest test_comparative_analyzer.py -v
```

## 📈 **Key Findings**

- **GFC ≈ COVID** (0.73 similarity) - Both crises, both QE
- **2022 ≈ Volcker** (0.68) - Both fighting inflation
- **Gradual tightening** - Most common pattern
- **Powell fastest** - COVID cuts in 13 days
- **Front-loading works** - 2022 75bp hikes effective

## 🔗 **Integration**

```python
# With Document Processor
meetings = [analyze_fomc_minutes_tool(f) for f in files]
pattern = identify_pattern_tool(meetings)

# With Policy Analyzer
regime = detect_regime_changes_tool(meetings)
similar = find_similar_episodes_tool(current_episode)

# With Trend Tracker
cycles = detect_policy_cycles_tool(meetings)
comparison = compare_episodes_tool(ep1, ep2)
```

## 📦 **Files**

- comparative_analyzer_config.py (670 lines) - Episodes, chairs, patterns
- episode_comparator.py (380 lines) - Comparison logic
- pattern_matcher.py (420 lines) - Pattern identification
- cross_episode_analyzer.py (360 lines) - Multi-episode analysis
- comparative_analyzer_tools.py (500 lines) - 5 ADK tools
- comparative_analyzer_agent.py (340 lines) - Agent
- test_comparative_analyzer.py (520 lines) - Tests

**Total: ~3,600 lines | 5 tools | 13 episodes | 6 patterns | 5 chairs**
