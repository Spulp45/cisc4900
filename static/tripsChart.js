const speed_time = track_points.map((item) => ({
  x: new Date(item.timestamp).getTime(),
  y: item.speed,
}));

const ele_time = track_points.map((item) => ({
  x: new Date(item.timestamp).getTime(),
  y: item.ele,
}));

function getUnits() {
  return sessionStorage.getItem("units") || "metric";
}

function setUnits(unit) {
  sessionStorage.setItem("units", unit);
}

function formatValue(value, type, units) {
  if (value == null) return "";
  if (units === "raw") return value;

  switch (type) {
    case "speed":
      return units === "imperial"
        ? `${(value * 2.23694).toFixed(2)} mph`
        : `${(value * 3.6).toFixed(2)} km/h`;
    case "distance":
      return units === "imperial"
        ? `${(value * 0.000621371).toFixed(2)} mi`
        : `${(value / 1000).toFixed(2)} km`;
    case "elevation":
      return units === "imperial"
        ? `${(value * 3.28084).toFixed(2)} ft`
        : `${value.toFixed(2)} m`;
    case "time":
      const h = Math.floor(value / 3600);
      const m = Math.floor((value % 3600) / 60);
      const s = Math.floor(value % 60);
      return `${h}:${m.toString().padStart(2, "0")}:${s
        .toString()
        .padStart(2, "0")}`;
    case "timestamp":
      return new Date(value).toLocaleTimeString();
    default:
      return value;
  }
}

const canvas1 = document.getElementById("tripsChart");

const myChart = new Chart(canvas1, {
  type: "line",
  data: {
    datasets: [
      {
        label:
          getUnits() === "imperial" ? "Speed (mph)" : "Speed (km/h)",
        data: speed_time,
        borderColor: "red",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      legend: { display: true },
      tooltip: {
        callbacks: {
          label: function (context) {
            const units = getUnits();
            const type = context.dataset.label.toLowerCase().includes("speed")
              ? "speed"
              : "misc";
            return formatValue(context.raw.y, type, units);
          },
        },
      },
      zoom: {
        pan: { enabled: true, mode: "x" },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: "x",
        },
      },
    },
    scales: {
      x: {
        type: "linear",
        title: { display: true, text: "Time" },
        ticks: {
          callback: function (value) {
            return formatValue(value, "timestamp", getUnits());
          },
        },
      },
      y: {
        title: { display: true, text: "Speed" },
        ticks: {
          callback: function (value) {
            return formatValue(value, "speed", getUnits());
          },
        },
      },
    },
  },
});

const canvas2 = document.getElementById("tripsChart2");

const myChart2 = new Chart(canvas2, {
  type: "line",
  data: {
    datasets: [
      {
        label:
          getUnits() === "imperial"
            ? "Elevation (ft)"
            : "Elevation (m)",
        data: ele_time,
        borderColor: "blue",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    interaction: {
      intersect: false,
      mode: "index",
    },
    plugins: {
      legend: { display: true },
      tooltip: {
        callbacks: {
          label: function (context) {
            const units = getUnits();
            const type = context.dataset.label
              .toLowerCase()
              .includes("elevation")
              ? "elevation"
              : "misc";
            return formatValue(context.raw.y, type, units);
          },
        },
      },
      zoom: {
        pan: { enabled: true, mode: "x" },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: "x",
        },
      },
    },
    scales: {
      x: {
        type: "linear",
        title: { display: true, text: "Time" },
        ticks: {
          callback: function (value) {
            return formatValue(value, "timestamp", getUnits());
          },
        },
      },
      y: {
        title: { display: true, text: "Elevation" },
        ticks: {
          callback: function (value) {
            return formatValue(value, "elevation", getUnits());
          },
        },
      },
    },
  },
});