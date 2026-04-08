
const dataPoints = track_points.map(item => ({
  x: new Date(item.timestamp).getTime(), 
  y: item.speed
}));


const totalDuration = 10000;
const delayBetweenPoints = totalDuration / dataPoints.length;

const previousY = (ctx) => {
  if (ctx.index === 0) {
    return ctx.chart.scales.y.getPixelForValue(0);
  }
  return ctx.chart
    .getDatasetMeta(ctx.datasetIndex)
    .data[ctx.index - 1]
    .getProps(['y'], true).y;
};


const canvas = document.getElementById('tripsChart');

const myChart = new Chart(canvas, {
  type: 'line',

  data: {
    datasets: [{
      label: 'Speed',
      data: dataPoints,
      borderColor: 'lime',
      borderWidth: 2,
      pointRadius: 0,
      tension: 0.3
    }]
  },

  options: {
    responsive: true,

    interaction: {
      intersect: false,
      mode: 'index'
    },

    plugins: {
      legend: {
        display: false
      }
    },

    scales: {
      x: {
        type: 'linear',
        title: {
          display: true,
          text: 'Time'
        },
        ticks: {
          callback: function(value) {
            const date = new Date(value);
            return date.toLocaleTimeString();
          }
        }
      },

      y: {
        title: {
          display: true,
          text: 'Speed'
        }
      }
    }
  }
});

