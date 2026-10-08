// Loads chart data from the REST API and draws the three dashboard charts.
(function () {
  const COLORS = ["#0f766e", "#2563eb", "#d97706", "#7c3aed", "#dc2626", "#059669", "#db2777", "#4b5563", "#0891b2"];

  async function getJSON(url) {
    const response = await fetch(url, { credentials: "same-origin" });
    if (!response.ok) {
      throw new Error("Request failed: " + url + " (" + response.status + ")");
    }
    return response.json();
  }

  async function drawCategoryChart() {
    const data = await getJSON("/api/spending/categories/");
    if (data.length === 0) {
      document.getElementById("categoryEmpty").classList.remove("d-none");
      return;
    }
    new Chart(document.getElementById("categoryChart"), {
      type: "doughnut",
      data: {
        labels: data.map((row) => row.category),
        datasets: [{ data: data.map((row) => row.total), backgroundColor: COLORS }],
      },
      options: { maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
    });
  }

  async function drawMonthlyCharts() {
    const data = await getJSON("/api/spending/monthly/");
    const labels = data.map((row) => row.label);
    const totals = data.map((row) => row.total);

    new Chart(document.getElementById("monthlyChart"), {
      type: "bar",
      data: { labels: labels, datasets: [{ label: "Spent (₹)", data: totals, backgroundColor: "#0f766e" }] },
      options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });

    new Chart(document.getElementById("trendChart"), {
      type: "line",
      data: {
        labels: labels,
        datasets: [{ label: "Spent (₹)", data: totals, borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,0.1)", fill: true, tension: 0.3 }],
      },
      options: { maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } },
    });
  }

  drawCategoryChart().catch(console.error);
  drawMonthlyCharts().catch(console.error);
})();
