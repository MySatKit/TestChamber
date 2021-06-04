async function getNewData(){
    let response = await fetch('/update');
    if (!response.ok) {
        console.log(`HTTP error! status: ${response.status}`);
    } else {
        updateBME(response.json());
    }
};

function updateBME(response){
    document.getElementById("it").textContent = response['inside']['temperature'] + " " + String.fromCharCode(176) + "C";
    document.getElementById("ot").textContent = response['outside']['temperature'] + " " + String.fromCharCode(176) + "C";
    document.getElementById("thc").textContent = response['thermocouple'] + " " + String.fromCharCode(176) + "C";

    document.getElementById("ip").textContent = response['inside']['pressure'] + " hPa";
    document.getElementById("op").textContent = response['outside']['pressure'] + " hPa";

    document.getElementById("ih").textContent = response['inside']['humidity'] + " %";

    let atmospheric = response['inside']['pressure'];
    let seaLevel = response['outside']['pressure'];
    document.getElementById("alt").textContent = (44330.0 * (1.0 - Math.pow(atmospheric / seaLevel, 0.1903))).toFixed(3) + " m";
};


document.addEventListener('DOMContentLoaded', function(){
    setInterval(() => getNewData(), 5000); // Milliseconds
});