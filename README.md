# Classroom Seat Planner

An AI-powered seating arrangement tool using Hill Climbing search.

## What it does

Enter plain English constraints for 10 students (A–J) and the AI finds the best seating layout for a 2×5 classroom grid.

**Supported constraints:**
- `A and B are friends` — seat them adjacent
- `A and D are not friends` — keep them apart
- `C wants front` — place in front row
- `E wants back` — place in back row
- `F needs teacher visibility` — place in front row
- `G is normal` — no preference

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:10000`

## Deploy

Hosted on [Render](https://ai-classroom-seating-arrangement.onrender.com/). Any push to the connected GitHub repo auto-deploys.

## Stack

- **Backend:** Python + Flask
- **Algorithm:** Hill Climbing (penalty-based scoring)
- **Frontend:** HTML, CSS, vanilla JS
