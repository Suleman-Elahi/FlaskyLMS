function updateStatus() {
  $('table').addClass('blurred');
  document.querySelector("#circle").style.display = 'block';
  // get all the table cells that contain a select input
  var cells = document.querySelectorAll("td select");
  
  // create a new array to hold the data
  var data = [];
  
  // iterate over each cell and add its data to the array
  for (var i = 0; i < cells.length; i++) {
    var cell = cells[i];
    var selectedValue = cell.value;
    
    // get the email address from the cell with id "email"
    var emailCell = cell.closest("tr").querySelector("#email");
    var email = emailCell.textContent.trim();
    
    // add the data to the array
    data.push({
      "email": email,
      "status": selectedValue
    });
  }

  // create a new FormData object and append the data to it
  var formData = new FormData();
  formData.append("data", JSON.stringify(data));
  
  // send a POST request to the /submit endpoint with the FormData object
  fetch("/submit", {
    method: "POST",
    body: formData
  }).then(response => {
    if (response.ok) {
      // reload the page to see the updated status values
        document.querySelector("#circle").style.display = "none";
        $('table').removeClass('blurred');
        alert("Leaves processed");
         location.reload();  
    } else {
      console.log("Error updating status: " + response.status);
    }

  }).catch(error => {
    console.log("Error updating status: " + error);
  });
}

