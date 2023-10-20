window.addEventListener("DOMContentLoaded", function() {
    var deleteButtons = document.getElementsByClassName("del-btn"); // select all the elements with the del-btn class
    for (var i = 0; i < deleteButtons.length; i++) { // loop through the array-like object
      var deleteButton = deleteButtons[i]; // get the current element
      deleteButton.addEventListener("click", function() { // add a click event listener
        return confirm("Are you sure?"); // show a confirmation dialog and return its result
      });
    }
  });

