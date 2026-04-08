import re
import os
import random
import heapq
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

ALL_ENTITIES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def parse_constraints(text):
    constraints = []
    for line in text.strip().splitlines():
        low = line.strip().lower()
        if not low:
            continue

        names = [s.upper() for s in re.findall(r'\b([a-z])\b', low)]

        if ("together" in low or "friend" in low) and len(names) >= 2:
            constraints.append({"type": "together", "entities": names[:2]})

        elif "not" in low and len(names) >= 2:
            constraints.append({"type": "not_together", "entities": names[:2]})

        elif "front" in low:
            for s in names:
                constraints.append({"type": "front", "entities": [s]})

        elif "back" in low:
            for s in names:
                constraints.append({"type": "back", "entities": [s]})

        elif "middle" in low:
            for s in names:
                constraints.append({"type": "middle", "entities": [s]})

    return constraints


def adjacent(i, j, cols):
    ri, ci = divmod(i, cols)
    rj, cj = divmod(j, cols)
    return abs(ri - rj) + abs(ci - cj) == 1


def calc_score(arr, constraints, rows, cols):
    penalty = 0

    for c in constraints:
        t = c["type"]
        e = c["entities"]

        if t == "together":
            a, b = e
            if not adjacent(arr.index(a), arr.index(b), cols):
                penalty += 3

        elif t == "not_together":
            a, b = e
            if adjacent(arr.index(a), arr.index(b), cols):
                penalty += 5

        elif t == "front":
            if arr.index(e[0]) >= cols:
                penalty += 4

        elif t == "back":
            if arr.index(e[0]) < (rows - 1) * cols:
                penalty += 4

        elif t == "middle":
            r = arr.index(e[0]) // cols
            if r == 0 or r == rows - 1:
                penalty += 3

    return penalty


# ---------------- HILL CLIMB ----------------
def hill_climb(entities, constraints, rows, cols, iterations=300):
    best = random.sample(entities, len(entities))
    best_score = calc_score(best, constraints, rows, cols)

    for _ in range(iterations):
        candidate = best[:]
        i, j = random.sample(range(len(entities)), 2)
        candidate[i], candidate[j] = candidate[j], candidate[i]

        s = calc_score(candidate, constraints, rows, cols)

        if s <= best_score:
            best, best_score = candidate, s

        if best_score == 0:
            break

    return best, best_score


# ---------------- A* (limited) ----------------
def astar(entities, constraints, rows, cols, max_visited=300, neighbors=3):
    """
    max_visited  — stop after exploring this many states (was unlimited)
    neighbors    — generate this many swaps per state (was 5)
    Both limits make A* faster with a small accuracy tradeoff.
    """
    start = entities[:]
    random.shuffle(start)

    counter = 0  # tiebreaker so lists are never compared directly
    pq = []
    heapq.heappush(pq, (0, counter, start))

    visited = set()
    best_state = start
    best_score = calc_score(start, constraints, rows, cols)

    while pq:
        cost, _, state = heapq.heappop(pq)
        key = tuple(state)

        if key in visited:
            continue
        visited.add(key)

        if len(visited) > max_visited:
            break

        score = calc_score(state, constraints, rows, cols)

        if score < best_score:
            best_score = score
            best_state = state

        if score == 0:
            return state, score

        for _ in range(neighbors): 
            new = state[:]
            i, j = random.sample(range(len(entities)), 2)
            new[i], new[j] = new[j], new[i]

            new_score = calc_score(new, constraints, rows, cols)
            counter += 1
            heapq.heappush(pq, (new_score, counter, new))

    return best_state, best_score

def tabu_search(entities, constraints, rows, cols, iterations=400, tabu_size=50):
    current = random.sample(entities, len(entities))
    current_score = calc_score(current, constraints, rows, cols)
 
    best = current[:]
    best_score = current_score
 
    tabu_list = []  # stores (i, j) swap pairs
 
    for _ in range(iterations):
        best_candidate = None
        best_candidate_score = float("inf")
        best_move = None
 
        # Evaluate 20 random neighbour swaps
        for _ in range(20):
            i, j = random.sample(range(len(entities)), 2)
            move = (min(i, j), max(i, j))
 
            candidate = current[:]
            candidate[i], candidate[j] = candidate[j], candidate[i]
            s = calc_score(candidate, constraints, rows, cols)
 
            # Allow if not tabu, OR if it beats global best (aspiration)
            if move not in tabu_list or s < best_score:
                if s < best_candidate_score:
                    best_candidate = candidate
                    best_candidate_score = s
                    best_move = move
 
        if best_candidate is None:
            continue
 
        current = best_candidate
        current_score = best_candidate_score
 
        # Add to tabu list, evict oldest if full
        tabu_list.append(best_move)
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)
 
        if current_score < best_score:
            best = current[:]
            best_score = current_score
 
        if best_score == 0:
            break
 
    return best, best_score


def explain(arr, constraints, rows, cols):
    out = []

    for c in constraints:
        t = c["type"]
        e = c["entities"]

        if t == "together":
            sat = adjacent(arr.index(e[0]), arr.index(e[1]), cols)
            out.append({"text": f"{e[0]} & {e[1]} together", "ok": sat})

        elif t == "not_together":
            sat = not adjacent(arr.index(e[0]), arr.index(e[1]), cols)
            out.append({"text": f"{e[0]} & {e[1]} not together", "ok": sat})

        elif t == "front":
            sat = arr.index(e[0]) < cols
            out.append({"text": f"{e[0]} front", "ok": sat})

        elif t == "back":
            sat = arr.index(e[0]) >= (rows - 1) * cols
            out.append({"text": f"{e[0]} back", "ok": sat})

        elif t == "middle":
            r = arr.index(e[0]) // cols
            sat = r != 0 and r != rows - 1
            out.append({"text": f"{e[0]} middle", "ok": sat})

    return out


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
 
    rows = int(data["rows"])
    cols = int(data["cols"])
    count = int(data["count"])
 
    entities = ALL_ENTITIES[:count]
    constraints = parse_constraints(data["constraints"])
 
    # Run all three algorithms in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        hc_future = executor.submit(hill_climb,  entities, constraints, rows, cols)
        as_future = executor.submit(astar,       entities, constraints, rows, cols)
        ts_future = executor.submit(tabu_search, entities, constraints, rows, cols)
 
        hc_arr, hc_score = hc_future.result()
        as_arr, as_score = as_future.result()
        ts_arr, ts_score = ts_future.result()
 
    def build_grid(arr):
        padded = arr + [""] * (rows * cols - len(arr))
        return [padded[i * cols:(i + 1) * cols] for i in range(rows)]
 
    return jsonify({
        "hc": {
            "grid": build_grid(hc_arr),
            "score": hc_score,
            "exp": explain(hc_arr, constraints, rows, cols)
        },
        "ac": {
            "grid": build_grid(as_arr),
            "score": as_score,
            "exp": explain(as_arr, constraints, rows, cols)
        },
        "ts": {
            "grid": build_grid(ts_arr),
            "score": ts_score,
            "exp": explain(ts_arr, constraints, rows, cols)
        },
        "cols": cols
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
