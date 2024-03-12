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

// document.addEventListener('DOMContentLoaded', function() {
//   // Find all delete buttons in the document
//   document.querySelectorAll('.delete-btn').forEach(function(deleteBtn) {
//     deleteBtn.addEventListener('click', function(event) {
//       event.preventDefault(); // Prevent the default link behavior

//       // Show the confirmation dialog
//       var confirmed = confirm('Are you sure? Deleting the movie will delete all its reviews as well.');

//       if (confirmed) {
//         // Get the delete URL from the link's href attribute
//         var url = deleteBtn.href;

//         // Send a DELETE request using the fetch API
//         fetch(url, {
//           method: 'POST',
//           headers: {
//             'X-CSRFToken': '{{ csrf_token() }}' // Use the JavaScript variable
//           }
//         })
//         .then(function(response) {
//           // Handle the server response
//           if (response.ok) {
//             // Redirect or update the page as needed
//             window.location.reload();
//           } else {
//             console.error('Error:', error);
//             alert('An error occurred while deleting the movie.');
//           }
//         })
//         .catch(function(error) {
//           console.error('Error:', error);
//           alert('An error occurred while deleting the movie.');
//         });
//       }
//     });
//   });
// });


// document.addEventListener('DOMContentLoaded', function() {
//   // Find all delete buttons in the document
//   document.querySelectorAll('.inline-form').forEach(function(form) {
//       form.addEventListener('submit', function(event) {
//           // Prevent the form from submitting immediately
//           event.preventDefault();
          
//           // Show the confirmation dialog
//           var confirmed = confirm('Are you sure? Deleting the movie will delete all its reviews as well.');
          
//           if (confirmed) {
//               // Submit the form if the user confirmed
//               form.submit();
//           }
//       });
//   });
// });

// document.addEventListener('DOMContentLoaded', function() {
//   // Find all delete buttons in the document
//   document.querySelectorAll('.inline-form').forEach(function(form) {
//     form.addEventListener('submit', function(event) {
//       // Prevent the form from submitting immediately
//       event.preventDefault();

//       // Show the confirmation dialog
//       var confirmed = confirm('Are you sure? Deleting the movie will delete all its reviews as well.');
//       if (confirmed) {
//         // Get the form action URL
//         var url = form.action;

//         // Send a DELETE request using the fetch API
//         fetch(url, {
//           method: 'POST',
//           headers: {
//             'X-CSRFToken': '{{ csrf_token() }}' // Include the CSRF token if necessary
//           }
//         })
//         .then(function(response) {
//           // Handle the server response
//           if (response.ok) {
//             // Redirect or update the page as needed
//             window.location.reload();
//           } else {
//             alert('An error occurred while deleting the movie.');
//           }
//         })
//         .catch(function(error) {
//           console.error('Error:', error);
//           alert('An error occurred while deleting the movie.');
//         });
//       }
//     });
//   });
// });


// window.addEventListener("DOMContentLoaded", function() {
//     var deleteButtons = document.getElementsByClassName("del-btn"); // select all the elements with the del-btn class
//     for (var i = 0; i < deleteButtons.length; i++) { // loop through the array-like object
//       var deleteButton = deleteButtons[i]; // get the current element
//       deleteButton.addEventListener("click", function() { // add a click event listener
//         return confirm("Are you sure?"); // show a confirmation dialog and return its result
//       });
//     }
//   });

