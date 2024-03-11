// client-side timeout reset

let timeout;
document.onmousemove = function(){
  clearTimeout(timeout);
  timeout = setTimeout(function(){
    if (confirm("You've been inactive for a while. Click OK to stay logged in.")) {
      fetch('/reset-session', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data));
    }
  }, 600000*3); // 30 minutes
}

document.addEventListener('DOMContentLoaded', function() {
  // Find all delete buttons in the document
  document.querySelectorAll('.inline-form').forEach(function(form) {
      form.addEventListener('submit', function(event) {
          // Prevent the form from submitting immediately
          event.preventDefault();
          
          // Show the confirmation dialog
          var confirmed = confirm('Are you sure? Deleting the movie will delete all its reviews as well.');
          
          if (confirmed) {
              // Submit the form if the user confirmed
              form.submit();
          }
      });
  });
});


// window.addEventListener("DOMContentLoaded", function() {
//     var deleteButtons = document.getElementsByClassName("del-btn"); // select all the elements with the del-btn class
//     for (var i = 0; i < deleteButtons.length; i++) { // loop through the array-like object
//       var deleteButton = deleteButtons[i]; // get the current element
//       deleteButton.addEventListener("click", function() { // add a click event listener
//         return confirm("Are you sure?"); // show a confirmation dialog and return its result
//       });
//     }
//   });

