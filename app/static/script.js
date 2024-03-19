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

// Get the modal and its elements
var modal = document.getElementById("boardModal");
var closeBtn = document.getElementsByClassName("close")[0];
var selectBtn = document.getElementById("selectBoard");

// When the user clicks the "Add" button, open the modal
document.forms['movieForm'].addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    modal.style.display = "block"; // Show the modal
});

// When the user clicks on the close button, close the modal
closeBtn.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks outside the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Handle board selection
selectBtn.onclick = function() {
    // Get the selected board or new board name
    var boardId = document.querySelector('input[name="board_id"]:checked').value;
    var newBoardName = document.getElementById("new_board_name").value;

    // Check if creating a new board or using an existing one, and set appropriate form data
    var form = document.forms['movieForm'];
    if (newBoardName) {
      var newBoardInput = document.createElement('input');
      newBoardInput.type = 'hidden';
      newBoardInput.name = 'new_board_name';
      newBoardInput.value = newBoardName;
      form.appendChild(newBoardInput);
    } else if (boardId) {
      var boardIdInput = document.createElement('input');
      boardIdInput.type = 'hidden';
      boardIdInput.name = 'board_id';
      boardIdInput.value = boardId;
      form.appendChild(boardIdInput);
    }

    // // Add the selected board to the form data
    // var form = document.forms['movieForm'];
    // var boardInput = document.createElement('input');
    // boardInput.type = 'hidden';
    // boardInput.name = 'board_id';
    // boardInput.value = boardId || newBoardName;
    // form.appendChild(boardInput);

    // Submit the form
    form.submit();

    // Close the modal after successful submission
    modal.style.display = "none";
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

