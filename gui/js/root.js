async function getNewData(){
    let response = await fetch('/update');
    if (!response.ok) {
        console.log(`HTTP error! status: ${response.status}`);
    } else {
        data = await response.json()
        updateBME(data);
    }
};


async function toggleLN2(){
    let response = await fetch('/buttons/toggleLN2');
    let data = await response.json();
    let toggle_ln2_btn = document.getElementById("toggle_ln2");

    if (data["state"]) {
        toggle_ln2_btn.style["background-color"] = "green";
    } else {
        toggle_ln2_btn.style["background-color"] = "red";
    }
};


function updateBME(response){
    document.getElementById("it").textContent = response['inside']['temperature'] + " " + String.fromCharCode(176) + "C";
    document.getElementById("ot").textContent = response['outside']['temperature'] + " " + String.fromCharCode(176) + "C";
    document.getElementById("thc").textContent = response['thermocouple'] + " " + String.fromCharCode(176) + "C";

    document.getElementById("ip").textContent = response['inside']['pressure'] + " hPa";
    document.getElementById("op").textContent = response['outside']['pressure'] + " hPa";

    document.getElementById("oh").textContent = response['outside']['humidity'] + " %";

    let atmospheric = response['inside']['pressure'];
    let seaLevel = response['outside']['pressure'];
    document.getElementById("alt").textContent = (44330.0 * (1.0 - Math.pow(atmospheric / seaLevel, 0.1903))).toFixed(3) + " m";
};


document.addEventListener('DOMContentLoaded', function(){
    setInterval(() => getNewData(), 500); // Milliseconds

    let toggle_ln2_btn = document.getElementById("toggle_ln2");
    toggle_ln2_btn.addEventListener("click", toggleLN2);
});