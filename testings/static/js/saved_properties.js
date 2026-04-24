const amount = document.getElementById("amount");
const rate = document.getElementById("rate");
const time = document.getElementById("time");

const amtVal = document.getElementById("amtVal");
const rateVal = document.getElementById("rateVal");
const timeVal = document.getElementById("timeVal");

function formatNumber(num) {
    return Number(num).toLocaleString("en-IN");
}

function calculateEMI() {
    let P = Number(amount.value);
    let r = Number(rate.value) / 12 / 100;
    let n = Number(time.value);

    let emi;
    if (r === 0) {
        emi = P / n;
    } else {
        emi = (P * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
    }

    document.getElementById("emi").innerText =
        "Monthly EMI: ₹ " + formatNumber(emi.toFixed(0));

    document.getElementById("total").innerText =
        "Total Payment: ₹ " + formatNumber((emi * n).toFixed(0));

    document.getElementById("interest").innerText =
        "Total Interest: ₹ " + formatNumber(((emi * n) - P).toFixed(0));
}

/* 🔥 SINGLE EVENT HANDLER (IMPORTANT) */
function updateValues() {
    amtVal.innerText = formatNumber(amount.value);
    rateVal.innerText = rate.value;
    timeVal.innerText = time.value;
    calculateEMI();
}

amount.addEventListener("input", updateValues);
rate.addEventListener("input", updateValues);
time.addEventListener("input", updateValues);

/* ✅ RUN ON LOAD */
window.onload = updateValues;