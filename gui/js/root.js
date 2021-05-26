function getNewData(){
    fetch('/update')
        .then((response) => {
            return response.json();
        })
         // uncomment to log
        .then((data) => {
            console.log(data);
        });
};

function updateBME(response){
    // will implement it soon
};


document.addEventListener('DOMContentLoaded', function(){
    setTimeout(() => updateBME(getNewData()), 5000); // Milliseconds
    /*
    1 - бесконечный цикл
    2 - задержка
    */
});