document.addEventListener("DOMContentLoaded", function() {
    var updat = setInterval(updateprice , 15000);
    function updateprice() {
        document.querySelectorAll(".updateP").forEach((element) =>{
            //console.log(element.id);
            fetch(`/coincall/${element.id}`)
            .then(response => response.json())
            .then((data)=> {
            element.innerHTML= data.price;

            curclr = element.style.color;
            element.style.color = 'green'
            setTimeout(() => {
                element.style.color = curclr
            }, 500);
            })
            .catch(error => {
                console.log("Error", error);
            })
        })
    }
    var updat = setInterval(updatecoinpage , 10000);
    function updatecoinpage() {
        document.querySelectorAll(".coinpageprice").forEach((element) =>{
            fetch(`/coincall/${element.id}`)
                .then(response => response.json())
                .then((data)=> {
                element.innerHTML= data.price;

                curclr = element.style.color;
                element.style.color = 'green'
                setTimeout(() => {
                    element.style.color = curclr
                }, 500);
            })
            .catch(error => {
                console.log("Error", error);
            })
        })
        console.log("UPDATED");
        //return false;
    }

    var modal = document.getElementById("myModal");
    var span = document.getElementsByClassName("close")[0];
    span.onclick = function() {
        modal.style.display = "none";
    }
    window.onclick = function(event) {
        if (event.target == modal) {
          modal.style.display = "none";
        }
    }
})