# 🎓 Study Plan Optimizer — Hackathon Pitch Deck

---

## 📌 Slide 1: Title & Team
### **Study Plan Optimizer**
#### *Algorithmic Study Schedule Optimization Using Data Structures & Algorithms*
- **Domain:** Data Structures & Algorithms (DSA) / Educational Technology
- **Tech Stack:** Python 3.11+, Streamlit, Plotly, NumPy, Pandas
- **Target Audience:** College students preparing for exams under strict time constraints

---

## 📌 Slide 2: Problem Statement
- **The Core Dilemma:** Before exams, college students typically have **limited study hours** (e.g., 10–20 hours) but an overwhelming syllabus (20–40 topics across 5+ subjects).
- **Suboptimal Choices:** Students either get stuck spending too much time on low-yield topics, or freeze from cognitive overload trying to prioritize.
- **Goal:** Select the optimal subset of topics such that:
  $$\sum \text{Study Time} \le \text{Available Time}$$
  while maximizing:
  $$\sum \text{Expected Score Improvement / Learning Benefit}$$

---

## 📌 Slide 3: Existing Problem (Current Approaches)
- **Intuition-Based / Random Selection:** Studying whatever chapter is opened first, ignoring return on time invested.
- **Ignoring Preparation Gaps:** Spending hours re-reading topics already mastered (e.g., 90% prepared), missing out on low-hanging high-yield topics (e.g., 20% prepared).
- **Flawed Prerequisite Flow:** Attempting advanced topics (e.g., Dynamic Programming or Graph BFS) without fundamental prerequisites (Recursion, Arrays).
- **Rigid Timetables:** Static calendars fail when real available hours change from 15 hours to 8 hours before test day.

---

## 📌 Slide 4: Our Solution
- **Mathematical Modeling as a 0/1 Knapsack Problem:**
  - **Knapsack Capacity ($W$):** Available study hours.
  - **Item Weight ($w_i$):** Estimated study duration.
  - **Item Value ($v_i$):** Multi-factor Expected Benefit Score.
- **Pure Algorithmic Engine:** Implemented with foundational DSA — zero black-box third-party optimization solvers!
- **Interactive Multi-Model Comparison:** Compares Dynamic Programming, Greedy Value Density, and Priority Queue.
- **End-to-End Execution:** From mathematical topic scoring to day-wise Pomodoro session scheduling.

---

## 📌 Slide 5: How the Optimizer Works (Mathematical Model)
1. **Preparation Gap:**
   $$\text{Gap} = \frac{100 - \text{Current Prep}}{100}$$
2. **Normalized Multi-Factor Scoring:**
   $$\text{Benefit Score} = \text{Marks} \times \left(\frac{\text{Importance}}{10}\right)^{w_i} \times \text{Gap}^{w_g} \times \left(\frac{\text{Priority}}{10}\right)^{w_p} \times \text{Difficulty Multiplier}$$
3. **Value Density (ROI per hour):**
   $$\text{Value Density} = \frac{\text{Benefit Score}}{\text{Study Time (hrs)}}$$
4. **Algorithmic Selection & Topological Sequencing:**
   Sorts and filters topics while enforcing prerequisite DAG ordering.

---

## 📌 Slide 6: DSA Concepts Used
| Data Structure / Algorithm | Practical Purpose in Project |
| :--- | :--- |
| **2D Dynamic Programming Array** | Memoization table for 0/1 Knapsack optimal subset selection |
| **Max-Heap (Binary Tree Array)** | Priority Queue with $O(\log N)$ extraction for dynamic yield prioritization |
| **Directed Acyclic Graph (DAG)** | Modeling topic prerequisites and course dependencies |
| **Topological Sort (Kahn's BFS)** | Sequencing selected study topics so fundamentals precede advanced topics |
| **Binary Search on Answer** | Finding minimum hours needed to attain target exam marks |
| **Hash Tables / Dictionaries** | $O(1)$ fast lookup for topic metrics, dependencies, and state |

---

## 📌 Slide 7: Algorithm 1 — Greedy Approach
- **Strategy:** Return-On-Investment (Value Density) heuristic.
- **Algorithm:**
  1. Calculate $\text{Density}_i = \frac{\text{Benefit}_i}{\text{Time}_i}$ for all $i \in [1..N]$.
  2. Sort topics in descending order of Value Density.
  3. Greedily select topics if $\text{Time} \le \text{Remaining Budget}$.
- **Complexity:**
  - **Time:** $O(N \log N)$ (sorting)
  - **Space:** $O(N)$
- **Pros & Cons:** Extremely fast ($< 1$ ms), but may leave slack capacity unused because it cannot backtrack.

---

## 📌 Slide 8: Algorithm 2 — Dynamic Programming (0/1 Knapsack)
- **Strategy:** Exact global optimum via Bellman's principle of optimality.
- **Recurrence Relation:**
  $$dp[i][w] = \begin{cases} dp[i-1][w] & \text{if } w_i > w \\ \max(dp[i-1][w], dp[i-1][w - w_i] + b_i) & \text{otherwise} \end{cases}$$
- **Backtracking:** Traces from $dp[N][W]$ backwards to recover the exact set of chosen topics.
- **Complexity:**
  - **Time:** $O(N \times W)$ (pseudo-polynomial)
  - **Space:** $O(N \times W)$
- **Pros & Cons:** Mathematically proven global maximum benefit for discrete capacity; higher memory requirement than greedy.

---

## 📌 Slide 9: Algorithm 3 — Priority Queue (Max Heap)
- **Strategy:** Dynamic prioritization using pure array-based Max-Heap.
- **Heap Invariant:** Parent key $\ge$ Child keys, where key is $(\text{Value Density}, \text{Exam Priority}, \text{Marks})$.
- **Operations:**
  - `insert()`: Appends and executes `_sift_up()` in $O(\log N)$.
  - `extract_max()`: Swaps root with last leaf and executes `_sift_down()` in $O(\log N)$.
- **Dynamic Prioritization:** Adaptively prioritizes topics whose prerequisites are satisfied.
- **Complexity:** $O(N \log N)$ total time, $O(N)$ space.

---

## 📌 Slide 10: System Architecture
```
Study Plan Optimizer Architecture
├── UI Layer (Streamlit)
│   ├── Interactive Dashboard & Visualizations (Plotly)
│   ├── Topic Input & Management Table
│   ├── Algorithm Comparison Lab & DP Table Heatmap
│   └── Pomodoro Timetable & Daily Schedule
├── Service Layer
│   ├── StudyOptimizerService (Orchestrator & What-If Engine)
│   ├── ScoringService (Benefit & Explainability Generator)
│   └── SchedulerService (Chronological Timetable Generator)
├── Algorithmic Engine (Pure Python DSA)
│   ├── 0/1 Knapsack Dynamic Programming + Backtracking
│   ├── Greedy Value Density Selection
│   ├── MaxHeap Priority Queue
│   ├── DependencyGraph (DAG + Topological Sort)
│   └── Binary Search on Answer
└── Data & Validation Layer
    ├── Topic & Student Profile Dataclasses
    ├── Strict Bound & Cycle Validators
    └── Realistic 20-Topic Engineering Dataset
```

---

## 📌 Slide 11: Live Demo Highlights
1. **Interactive Dashboard:** Live summary of target score, study budget, and topic inventory.
2. **Multi-Model Optimization:** Instant execution of DP, Greedy, and Max-Heap with execution time down to milliseconds.
3. **Transparent Explainability:** Bulleted reasons for every selected and omitted topic.
4. **Visual DP Matrix:** Inspection of Dynamic Programming decision grid.
5. **Pomodoro Day Planner:** Realistic study blocks (50m) and rest intervals (10m).

---

## 📌 Slide 12: Experimental Results & Comparison
- Tested on standard 20-topic CS syllabus across 10h, 15h, and 20h budgets:
  - **Dynamic Programming:** Always yields the mathematical upper bound for expected benefit.
  - **Greedy:** Achieves 92%–97% of optimal DP benefit in $\sim 0.2$ ms.
  - **Priority Queue:** Matches greedy efficiency while providing flexible stream-based scheduling.
- **What-If Curve:** Proves the law of diminishing returns — initial 8 hours provide over 60% of total possible score yield!

---

## 📌 Slide 13: Future Scope & Roadmap
1. **Machine Learning Calibration:** Train personal difficulty and retention curves based on actual test scores.
2. **Spaced Repetition Integration (Anki / SM-2):** Algorithmic scheduling of review sessions at increasing intervals.
3. **Calendar Sync:** Direct export to Google Calendar and iCal via ICS files.
4. **Multi-Student Collaborative Study:** Bipartite matching or Coalition Game Theory for study group formation.

---

## 📌 Slide 14: Conclusion
- **Study Plan Optimizer** bridges abstract algorithmic theory and everyday student life.
- Demonstrates mastery of **Dynamic Programming, Greedy Algorithms, Heaps, Topological Sorting, and Binary Search**.
- Built with clean, tested, modular, production-ready Python code.
- Empowers students to **study smarter, not just longer**!
