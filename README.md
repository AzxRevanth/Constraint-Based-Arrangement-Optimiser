# Constraint-Based Arrangement Optimizer

A web-based system that solves arrangement problems using search-based optimization techniques. The system takes user-defined conditions in simple text form and generates an optimized arrangement while minimizing constraint violations.

---

## Overview

This project focuses on arranging a set of entities within a grid while satisfying a set of conditions. These conditions may include:
- placing entities together  
- keeping entities apart  
- assigning position preferences  

Since many conditions can conflict, the system treats this as an optimization problem. Instead of trying to satisfy all constraints perfectly, it finds the best possible arrangement with the least number of violations.

The system applies multiple search algorithms and compares their outputs.

---

## Features

- Accepts constraints in simple natural language  
- Supports multiple constraint types:
  - together  
  - not together  
  - front  
  - middle  
  - back  
- Uses a penalty-based scoring system  
- Runs multiple algorithms in parallel  
- Displays results side by side for comparison  
- Provides explanation of satisfied and violated constraints  

---

## Algorithms Used

### Hill Climbing
- Starts with a random arrangement  
- Makes small changes by swapping elements  
- Accepts changes if they improve or maintain the score  
- Fast but can get stuck in local optima  

### Tabu Search
- Uses memory (tabu list) to avoid repeating recent moves  
- Explores a wider solution space  
- More reliable for complex constraint sets  

### A* Search
- Uses a priority queue to explore better states first  
- Evaluates arrangements based on penalty score  
- Limited search to keep runtime manageable  

---

## How It Works

1. User enters constraints in text form  
2. Constraints are parsed into structured rules  
3. Initial arrangement is generated  
4. Each algorithm explores possible arrangements  
5. Arrangements are scored using a penalty function  
6. Best results from each algorithm are returned  
7. Results are displayed with scores and explanations  

---

## Scoring System

- Each constraint violation adds a penalty  
- Lower score means a better arrangement  
- Score of 0 means all constraints are satisfied  

---

## Tech Stack

- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, JavaScript  
- **Concurrency:** ThreadPoolExecutor  
- **Deployment:** Render  

---

## Running Locally

```bash
git clone https://github.com/AzxRevanth/Constraint-Based-Arrangement-Optimiser
cd Constraint-Based-Arrangement-Optimiser
pip install -r requirements.txt
python app.py
