function generate() {
  const btn = document.getElementById("btn-text");
  btn.textContent = "Running...";

  fetch("/generate", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      rows:        document.getElementById("rows").value,
      cols:        document.getElementById("cols").value,
      count:       document.getElementById("count").value,
      constraints: document.getElementById("constraints").value
    })
  })
  .then(res => res.json())
  .then(data => {
    render("hc", data.hc, data.cols);
    render("ac", data.ac, data.cols);   
    render("ts", data.ts, data.cols);
    btn.textContent = "Generate";
  })
  .catch(() => {
    btn.textContent = "Generate";
  });
}

function render(prefix, data, cols) {
  const grid = document.getElementById(prefix + "-grid");
  grid.innerHTML = "";
  grid.style.gridTemplateColumns = `repeat(${cols}, 46px)`;

  data.grid.flat().forEach(x => {
    const d = document.createElement("div");
    d.className = "seat";
    d.innerText = x;
    grid.appendChild(d);
  });

  document.getElementById(prefix + "-score").innerText = "Penalty Score: " + data.score;

  const expBox = document.getElementById(prefix + "-exp");
  expBox.innerHTML = "";

  data.exp.forEach(e => {
    const div = document.createElement("div");
    div.className = "exp-item " + (e.ok ? "pass" : "fail");
    div.innerText = (e.ok ? "✔  " : "✘  ") + e.text;
    expBox.appendChild(div);
  });
}