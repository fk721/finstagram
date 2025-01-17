// API CALL TO FLASK TO GET PHOTO INFO
function getInfo(photoID) {
    $.ajax({
        type: 'POST',
        url: "/get_info",
        data: photoID,
        success: function(response) {
            // console.log(response);
            var response = JSON.parse(response);
            var numLikes = response['numLikes'];
            var posterStats = response['posterStats'];
            var taggedUsers = JSON.parse(response['taggedUsers']);
            var likedUsers = JSON.parse(response['likedUsers']);

            var modal = document.getElementById("modal-body-" + photoID);

            var RES_HTML =
            "<strong> Number of Likes: </strong> " + numLikes + "<br>" +
            "<strong> Posted By: </strong>" + posterStats['firstName'] + " " + posterStats['lastName'] + "<br>";

            if (taggedUsers.length == 0) {
                RES_HTML += "<strong> Tagged Users: </strong> NONE";
                RES_HTML += "<br>";
            } else {
                RES_HTML += "<strong> Tagged Users: </strong>";
                RES_HTML += "<table class='table table-dark'> <tr> <th>Username</th> <th>First Name</th> <th>Last Name</th> </tr>";
                for (var i = 0; i < taggedUsers.length; i++) {
                    var curr = taggedUsers[i];
                    RES_HTML += "<tr><td>" + curr["username"] + "</td> <td>" + curr["firstName"] + "</td><td>" + curr["lastName"] + "</td></tr>";
                }
                RES_HTML += "</table>";
            } 

            if (likedUsers.length === 0) {
                RES_HTML += "<strong> Liked By Users: </strong> NONE";
            } else {
                RES_HTML += "<strong> Liked By Users: </strong>";
                RES_HTML += "<table class='table table-dark'> <tr> <th>Username</th> <th> Rating </th> </tr>";
                for (var i = 0; i < likedUsers.length; i++) {
                    var curr = likedUsers[i];
                    RES_HTML += "<tr><td>" + curr["username"] + "</td> <td>" + curr["rating"] + "</td></tr>";
                }
                RES_HTML += "</table>";
            }  

            modal.innerHTML = RES_HTML;
        },
        error: function(error) {
            console.log(error);
        }
    });
};

// API CALL TO FLASK TO PROCESS FOLLOW REQUESTS
function processFollowRequests() {
    var toAccept = [];
    var toDelete = [];
    $("input:radio.toAccept:checked").each(function () {
        toAccept.push(this.value);
    });

    $("input:radio.toDelete:checked").each(function () {
        toDelete.push(this.value);
    });

    $.ajax({
        type: 'POST',
        url: "/process_requests",
        data: {toAccept: JSON.stringify(toAccept), toDelete: JSON.stringify(toDelete)},
        success: function(response) {
            setTimeout(function(){// wait for 5 secs(2)
                location.reload(); // then reload the page.(3)
           }, 1500); 
        },
        error: function(error) {
            console.log(error);
        }
    });
}

// DISABLE FORM RESUBMISSION 

// if ( window.history.replaceState ) {
//     window.history.replaceState( null, null, window.location.href );
// }
