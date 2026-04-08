const speed_time = track_points.map((item) => ({
  x: new Date(item.timestamp).getTime(),
  y: item.speed,
}));

const ele_time = track_points.map((item) => ({
  x: new Date(item.timestamp).getTime(),
  y: item.ele,
}));

const canvas1 = document.getElementById("tripsChart");

const myChart = new Chart(canvas1, {
  type: "line",

  data: {
    datasets: [
      {
        label: "Speed",
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
            const date = new Date(value);
            return date.toLocaleTimeString();
          },
        },
      },
      y: {
        title: { display: true, text: "Speed" },
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
        label: "Elevation",
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
            const date = new Date(value);
            return date.toLocaleTimeString();
          },
        },
      },
      y: {
        title: { display: true, text: "Elevation" },
      },
    },
  },
});
