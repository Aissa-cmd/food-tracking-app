const tableFb = document.getElementById("foodtable-fb");
const tableLb = document.getElementById("foodtable-lb");
const tableDb = document.getElementById("foodtable-db");
const tableSn = document.getElementById("foodtable-sn");

let fbCalories = 0,
  fbFat = 0,
  fbCarbohydrates = 0,
  fbProtein = 0;

let lbCalories = 0,
  lbFat = 0,
  lbCarbohydrates = 0,
  lbProtein = 0;

let dbCalories = 0,
  dbFat = 0,
  dbCarbohydrates = 0,
  dbProtein = 0;

let snCalories = 0,
  snFat = 0,
  snCarbohydrates = 0,
  snProtein = 0;

// breakfast
for (var i = 1; i < tableFb.rows.length; i++) {
  fbCalories += parseFloat(tableFb.rows[i].cells[2].innerHTML);

  fbFat += parseFloat(tableFb.rows[i].cells[3].innerHTML);
  fbFat = Math.round(fbFat);

  fbCarbohydrates += parseFloat(tableFb.rows[i].cells[4].innerHTML);
  fbCarbohydrates = Math.round(fbCarbohydrates);

  fbProtein += parseFloat(tableFb.rows[i].cells[5].innerHTML);
  fbProtein = Math.round(fbProtein);
}

// lunch
for (var i = 1; i < tableLb.rows.length; i++) {
  lbCalories += parseFloat(tableLb.rows[i].cells[2].innerHTML);

  lbFat += parseFloat(tableLb.rows[i].cells[3].innerHTML);
  lbFat = Math.round(lbFat);

  lbCarbohydrates += parseFloat(tableLb.rows[i].cells[4].innerHTML);
  lbCarbohydrates = Math.round(lbCarbohydrates);

  lbProtein += parseFloat(tableLb.rows[i].cells[5].innerHTML);
  lbProtein = Math.round(lbProtein);
}

// dinner
for (var i = 1; i < tableDb.rows.length; i++) {
  lbCalories += parseFloat(tableDb.rows[i].cells[2].innerHTML);

  lbFat += parseFloat(tableDb.rows[i].cells[3].innerHTML);
  lbFat = Math.round(lbFat);

  lbCarbohydrates += parseFloat(tableDb.rows[i].cells[4].innerHTML);
  lbCarbohydrates = Math.round(lbCarbohydrates);

  lbProtein += parseFloat(tableDb.rows[i].cells[5].innerHTML);
  lbProtein = Math.round(lbProtein);
}

// snack
for (var i = 1; i < tableSn.rows.length; i++) {
  snCalories += parseFloat(tableSn.rows[i].cells[2].innerHTML);

  snFat += parseFloat(tableSn.rows[i].cells[3].innerHTML);
  snFat = Math.round(snFat);

  snCarbohydrates += parseFloat(tableSn.rows[i].cells[4].innerHTML);
  snCarbohydrates = Math.round(snCarbohydrates);

  snProtein += parseFloat(tableSn.rows[i].cells[5].innerHTML);
  snProtein = Math.round(snProtein);
}

// -------------------------------------------------------------------

// var table = document.getElementById("foodtable");
// var calories = 0,
//   fat = 0,
//   carbohydrates = 0,
//   protein = 0;

// for (var i = 1; i < table.rows.length - 1; i++) {
//   calories += parseFloat(table.rows[i].cells[1].innerHTML);

//   fat += parseFloat(table.rows[i].cells[2].innerHTML);
//   fat = Math.round(fat);

//   carbohydrates += parseFloat(table.rows[i].cells[3].innerHTML);
//   carbohydrates = Math.round(carbohydrates);

//   protein += parseFloat(table.rows[i].cells[4].innerHTML);
//   protein = Math.round(protein);
// }

// document.getElementById("totalCalories").innerHTML = "<b>" + calories + "</b>";
// document.getElementById("totalFat").innerHTML = "<b>" + fat + "</b>";
// document.getElementById("totalCarbohydrates").innerHTML =
//   "<b>" + carbohydrates + "</b>";
// document.getElementById("totalProtein").innerHTML = "<b>" + protein + "</b>";

// var total = fat + carbohydrates + protein;
const fatTotal = fbFat + lbFat + dbFat + snFat;
const carbsTotal =
  fbCarbohydrates + lbCarbohydrates + dbCarbohydrates + snCarbohydrates;
const proteinTotal = fbProtein + lbProtein + dbProtein + snProtein;
const total = fatTotal + carbsTotal + proteinTotal;

var fatPercentage = Math.round((fatTotal / total) * 100);
var carbohydratesPercentage = Math.round((carbsTotal / total) * 100);
var proteinPercentage = Math.round((proteinTotal / total) * 100);

fatPercentage = fatPercentage ? fatPercentage : 0;
carbohydratesPercentage = carbohydratesPercentage ? carbohydratesPercentage : 0;
proteinPercentage = proteinPercentage ? proteinPercentage : 0;

// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily =
  'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", "Liberation Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"';
Chart.defaults.global.defaultFontColor = "#858796";

// Doughnut Chart - Macronutrients breakdown
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: "doughnut",
  data: {
    labels: [
      "Fat " + fatPercentage + "%",
      "Carbs " + carbohydratesPercentage + "%",
      "Protein " + proteinPercentage + "%",
    ],
    datasets: [
      {
        data: [fatPercentage, carbohydratesPercentage, proteinPercentage],
        backgroundColor: ["#e5a641", "#55b560", "#419ad6"],
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    animation: {
      animateScale: true,
    },
    plugins: {
      legend: {
        display: true,
        position: "bottom",
      },
      title: {
        display: true,
        text: "Macronutrients Breakdown",
        font: {
          size: 20,
        },
      },
      datalabels: {
        display: true,
        color: "#fff",
        font: {
          weight: "bold",
          size: 16,
        },
        textAlign: "center",
      },
    },
  },
});

// Calorie Goal Progress Bar
const dailyCalories = parseFloat(
  document.getElementById("daily_calories").innerHTML
);
const exerciseCount = parseFloat(
  document.getElementById("exercise_count").innerHTML
);
const totalCalories123 = fbCalories + lbCalories + dbCalories + snCalories;
const totalCalories12 = totalCalories123 - exerciseCount;
var caloriePercentage = Math.round((totalCalories12 / dailyCalories) * 100);
//document.getElementById('progressBar').setAttribute('style', 'width:' + caloriePercentage + '%');

$(".progress-bar").animate(
  {
    width: caloriePercentage + "%",
  },
  500
);
var interval = setInterval(function () {
  $(".progress-bar").html(caloriePercentage + "%");
}, 500);

const daily_water_goal = parseFloat(
  document.getElementById("daily_water_goal").innerHTML
);

const water_consumption_count = parseFloat(
  document.getElementById("water_consumption_count").value
);

const waterPercentage = Math.round(
  (water_consumption_count / daily_water_goal) * 100
);

$(".progress-bar-water").animate(
  {
    width: waterPercentage + "%",
  },
  500
);
var intervalwater = setInterval(function () {
  $(".progress-bar-water").html(waterPercentage + "%");
}, 500);
