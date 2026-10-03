# 🎓 Study Plan Optimizer

> **Algorithmic Study Schedule Optimization Using Data Structures & Algorithms**  
> *Developed for College DSA Hackathon 2026*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![Visualizations](https://img.shields.io/badge/Charts-Plotly-orange.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-25%20Passed-brightgreen.svg)]()

---

## 📖 Table of Contents
1. [Problem Statement & Motivation](#-problem-statement--motivation)
2. [Core Mathematical Model](#-core-mathematical-model)
3. [Data Structures & Algorithms Implemented](#-data-structures--algorithms-implemented)
4. [Algorithm Deep-Dive & Complexity](#-algorithm-deep-dive--complexity)
5. [System Architecture](#-system-architecture)
6. [Project Structure](#-project-structure)
7. [Features & Functionality](#-features--functionality)
8. [Installation & Setup](#-installation--setup)
9. [How to Run](#-how-to-run)
10. [Sample Dataset & Example Walkthrough](#-sample-dataset--example-walkthrough)
11. [Unit Testing & Verification](#-unit-testing--verification)
12. [Hackathon Pitch Deck](#-hackathon-pitch-deck)
13. [Future Enhancements](#-future-enhancements)

---

## 🎯 Problem Statement & Motivation

During university exam seasons, engineering students face a persistent crisis: **too much syllabus and too little time**. 

### The Core Dilemma
A student typically has:
- **Available Study Time ($H$):** e.g., 10 to 20 hours.
- **Syllabus ($N$):** 20 to 40 topics spanning Data Structures, Operating Systems, DBMS, Networks, etc.
- **Unequal Topic Properties:** Different marks weightage, difficulty levels, subject importance, and student preparation gaps.

### Why Traditional Approaches Fail
- **Intuition-Based Selection:** Students pick whatever topic looks familiar or is first in the textbook.
- **Ignoring Preparation Gaps:** Spending hours re-reading topics already at 90% preparation yields minimal marginal marks improvement.
- **Prerequisite Violations:** Trying to learn Dynamic Programming without knowing Recursion or Graphs without Trees.
- **Non-Adaptive Schedules:** Static calendar templates break when available hours change.

### Our Objective
Model this dilemma as a **0/1 Knapsack Optimization Problem** using pure DSA:
$$\text{Maximize } \sum_{i \in S} \text{Expected Benefit Score}_i \quad \text{subject to} \quad \sum_{i \in S} \text{Study Time}_i \le \text{Available Hours}$$

---

## 📐 Core Mathematical Model

### 1. Preparation Gap
$$\text{Preparation Gap} = \frac{100 - \text{Current Prep}}{100} \in [0.0, 1.0]$$
*(A topic with 20% preparation has an 80% gap where new marks can be earned.)*

### 2. Multi-Factor Expected Benefit Score
$$\text{Benefit Score} = \text{Marks} \times \left(\frac{\text{Importance}}{10}\right)^{w_i} \times (\text{Prep Gap})^{w_g} \times \left(\frac{\text{Priority}}{10}\right)^{w_p} \times \text{Diff Multiplier}$$
Where:
- $\text{Importance} \in [1, 10]$: Exam frequency & syllabus weightage.
- $\text{Priority} \in [1, 10]$: Student focus / urgent exam targets.
- $\text{Diff Multiplier} = 1.0 + w_d \times \left(\frac{\text{Difficulty} - 5}{10}\right)$.
- $w_i, w_g, w_p, w_d$: Configurable exponent weights (defaults = 1.0).

### 3. Value Density (Yield per Hour)
$$\text{Value Density} = \frac{\text{Benefit Score}}{\text{Study Time (hrs)}}$$

---

## 🧠 Data Structures & Algorithms Implemented

| Category | DSA Component | Concrete Role in Project |
| :--- | :--- | :--- |
| **Data Structure** | `2D Array / Matrix` | Memoization table for 0/1 Knapsack Dynamic Programming |
| **Data Structure** | `Max-Heap` (Array-based) | Binary heap with `_sift_up` and `_sift_down` for priority scheduling |
| **Data Structure** | `Directed Acyclic Graph (DAG)` | Models topic prerequisites and course dependencies |
| **Data Structure** | `Hash Maps & Sets` | $O(1)$ fast lookups for topic IDs, visited sets, and in-degrees |
| **Algorithm** | `0/1 Knapsack (DP)` | Pseudo-polynomial exact globally optimal subset selection |
| **Algorithm** | `Greedy Approach` | Heuristic selection based on Value Density sorting |
| **Algorithm** | `Topological Sort (Kahn's BFS)` | Orders study topics so prerequisites precede advanced topics |
| **Algorithm** | `Cycle Detection` | Detects circular prerequisite dependencies in syllabus DAG |
| **Algorithm** | `Binary Search on Answer` | Finds minimum study hours required to reach a target score |

---

## 🔬 Algorithm Deep-Dive & Complexity

### 1. Dynamic Programming (0/1 Knapsack with Backtracking)
- **Concept:** Discretizes continuous study hours into integer steps (default 0.5h step $\to$ capacity $W = H \times 2$).
- **Recurrence Relation:**
  $$dp[i][w] = \begin{cases} dp[i-1][w] & \text{if } w_i > w \\ \max(dp[i-1][w], dp[i-1][w - w_i] + b_i) & \text{otherwise} \end{cases}$$
- **Backtracking:** Starting at $dp[N][W]$, traces backwards: if $dp[i][w] \neq dp[i-1][w]$, item $i$ was included and $w \leftarrow w - w_i$.
- **Complexity:**
  - **Time Complexity:** $O(N \times W)$
  - **Space Complexity:** $O(N \times W)$

### 2. Greedy Approach (Value Density)
- **Concept:** Calculates $\text{Density}_i = \frac{b_i}{t_i}$, sorts topics descending, and greedily selects items while remaining time allows.
- **Complexity:**
  - **Time Complexity:** $O(N \log N)$ (sorting)
  - **Space Complexity:** $O(N)$

### 3. Priority Queue (Max-Heap)
- **Concept:** Implemented from scratch using a list-backed binary heap:
  - Parent: `(i - 1) // 2`, Left: `2*i + 1`, Right: `2*i + 2`
  - Maintains composite key: `(Value Density, Priority, Expected Marks)`.
- **Complexity:**
  - **Build Heap:** $O(N)$
  - **Extraction:** $O(N \log N)$ for $N$ items
  - **Space Complexity:** $O(N)$

### 4. Dependency Graph & Topological Sort
- **Concept:** Uses Kahn's in-degree BFS queue algorithm to produce a valid sequence where prerequisites always precede dependent topics.
- **Complexity:**
  - **Time Complexity:** $O(V + E)$
  - **Space Complexity:** $O(V + E)$

---

## 🏛️ System Architecture

```text
Study Plan Optimizer
│
├── Presentation Layer (Streamlit UI & Plotly)
│   ├── Interactive Dashboard (KPIs, Donut & Scatter plots)
│   ├── Plan Optimizer (DP, Greedy, Heap runners + Explainability)
│   ├── Study Timetable (Pomodoro 50/10m Day-by-Day schedule)
│   ├── Algorithm Comparison Lab (DP Heatmap, Heap step trace)
│   ├── Analytics & What-If Analysis (Diminishing returns curves)
│   ├── Topic CRUD Manager
│   └── 14-Slide Hackathon Presentation Deck
│
├── Service Layer
│   ├── StudyOptimizerService (Coordinates algorithms & sweeps)
│   ├── ScoringService (Benefit score & explainability generator)
│   └── SchedulerService (Pomodoro clock session divider)
│
├── Algorithmic Engine (Pure Python Standard Library DSA)
│   ├── Dynamic Programming (0/1 Knapsack + Backtracking)
│   ├── Greedy Value Density
│   ├── MaxHeap Priority Queue
│   ├── DependencyGraph (DAG + Kahn's BFS Topological Sort)
│   └── Binary Search on Answer
│
└── Models & Data Layer
    ├── Topic & StudentProfile Dataclasses
    ├── Strict Bound & Cycle Validators
    └── Realistic 20-Topic Engineering Dataset
```

---

## 📂 Project Structure

```text
study-plan-optimizer/
│
├── app.py                      # Main Streamlit Web Application
├── requirements.txt            # Python dependencies
├── README.md                   # Complete documentation
│
├── algorithms/                 # Pure DSA implementations
│   ├── __init__.py
│   ├── result.py               # OptimizationResult dataclass
│   ├── dynamic_programming.py  # 0/1 Knapsack DP + Backtracking
│   ├── greedy.py               # Value Density Greedy algorithm
│   ├── priority_queue.py       # Custom MaxHeap & PQ solver
│   ├── dependency_graph.py     # DAG, Kahn's Topological Sort, Cycle Check
│   └── binary_search.py        # Classic BS & Binary Search on Answer
│
├── models/                     # Data entities
│   ├── __init__.py
│   ├── topic.py                # Topic dataclass with serialization
│   └── student.py              # StudentProfile dataclass
│
├── services/                   # Business & scheduling logic
│   ├── __init__.py
│   ├── scoring.py              # Benefit formula & explainability
│   ├── optimizer.py            # Orchestrator & what-if engine
│   └── scheduler.py            # Pomodoro timetable generator
│
├── utils/                      # Validation & IO helpers
│   ├── __init__.py
│   ├── validation.py           # Strict input boundary checkers
│   └── helpers.py              # JSON IO & time formatting
│
├── data/
│   └── sample_topics.json      # 20 realistic CS topics with prerequisites
│
├── presentation/
│   └── HACKATHON_SLIDES.md     # 14-slide presentation deck
│
└── tests/                      # Automated test suite (25 tests)
    ├── test_scoring.py
    ├── test_validation.py
    ├── test_dp.py
    ├── test_greedy.py
    ├── test_pq.py
    ├── test_graph.py
    ├── test_scheduler.py
    └── test_binary_search.py
```

---

## ✨ Features & Functionality

1. **Multi-Model Optimization:** Select between 0/1 Knapsack DP, Greedy Value Density, and Priority Queue Max-Heap.
2. **Explainability Engine:** Every topic includes explicit reasons for selection or omission (e.g. *High Marks: 15*, *Prep Gap: 75%*, *ROI: 4.2/hr*).
3. **Pomodoro Study Scheduler:** Automatically sections topics into 50-min study blocks and 10-min rest breaks across realistic calendar days.
4. **Prerequisite DAG Warnings:** Flags topics selected without adequate preparation in prerequisite topics.
5. **Interactive DP Heatmap:** Visualizes the 2D Dynamic Programming matrix $(N \times W)$ showing optimal substructure accumulation.
6. **Binary Search on Answer:** Calculates the exact minimum study hours needed to achieve a target score threshold.
7. **What-If Sensitivity Analysis:** Plots diminishing returns curve from 2 to 30 study hours.
8. **Built-in Hackathon Deck:** 14-slide pitch deck embedded directly inside the application for judging.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11, 3.12, or 3.13 installed.

### Setup Instructions
1. Navigate to the project directory:
   ```bash
   cd "C:\Users\AKULA VAMSHI VARDHAN\.gemini\antigravity\scratch\study-plan-optimizer"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 How to Run

Launch the Streamlit web application:
```bash
python -m streamlit run app.py
```

Open your web browser at:
```text
http://localhost:8501
```

---

## 🧪 Unit Testing & Verification

Run the comprehensive pytest test suite covering all algorithms, edge cases, and constraints:

```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- **Scoring:** Tests 0% prep, 100% prep, baseline revision yield, difficulty multipliers.
- **DP 0/1 Knapsack:** Tests optimal subsets, 0 available hours, excess hours, empty topic list, integer step discretization.
- **Greedy:** Tests value density ordering, equal-density ties, budget saturation.
- **Max-Heap:** Tests heap invariant, sift-up, sift-down, extract-max ordering, peek operations.
- **Dependency Graph:** Tests Kahn's topological sort, circular dependency cycle detection, missing prerequisite warnings.
- **Scheduler:** Tests Pomodoro slot division, multi-day capacity constraints, break insertion.
- **Binary Search:** Tests value density lookup and binary search on answer for target marks.

---

## 📊 Sample Input & Output Walkthrough

### Sample Input
- **Available Hours:** 10.0 hours
- **Daily Capacity:** 4.0 hours/day
- **Topic Pool:** 20 topics across Data Structures, Algorithms, OS, DBMS, Networks.

### Sample Optimization Result (Dynamic Programming)
- **Selected Topics (4 topics, 9.5 hours):**
  1. `Arrays & Strings Manipulation` (2.0 hrs | +6.2 benefit)
  2. `Recursion & Backtracking` (3.0 hrs | +11.4 benefit)
  3. `Dynamic Programming (Knapsack & LCS)` (4.5 hrs | +18.2 benefit)
- **Total Expected Marks Gain:** 38.0 marks
- **Total Expected Benefit:** 35.8
- **Execution Time:** ~1.4 ms

### Sample Pomodoro Timetable (Day 1)
```text
09:00 - 09:50  Arrays & Strings (Part 1/2)   [Study - 50m]
09:50 - 10:00  Rest & Recharge               [Break - 10m]
10:00 - 10:50  Arrays & Strings (Part 2/2)   [Study - 50m]
10:50 - 11:00  Rest & Recharge               [Break - 10m]
11:00 - 11:50  Recursion (Part 1/3)          [Study - 50m]
11:50 - 12:10  Recharge Break                [Long Break - 20m]
12:10 - 13:00  Recursion (Part 2/3)          [Study - 50m]
```

---

## 🔮 Future Enhancements
1. **Ebbinghaus Forgetting Curve Integration:** Dynamic decay modeling for retention loss over time.
2. **Calendar Export (.ics):** One-click synchronization with Google Calendar and Apple Calendar.
3. **Anki Flashcard Spaced Repetition Link:** Auto-generation of flashcard decks for selected topics.
4. **Peer Study Group Matching:** Bipartite graph matching for students with complementary topic preparations.

---

## 👨‍💻 Hackathon Presentation Deck
The full 14-slide presentation is available in [`presentation/HACKATHON_SLIDES.md`](presentation/HACKATHON_SLIDES.md) and can also be browsed interactively within the web application under the **🎯 Hackathon Slides** tab!
