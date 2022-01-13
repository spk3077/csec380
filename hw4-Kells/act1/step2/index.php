<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <title> Client Information</title>

        <!-- Matomo -->
        <script>
        var _paq = window._paq = window._paq || [];
        /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
        _paq.push(['trackPageView']);
        _paq.push(['enableLinkTracking']);
        (function() {
            var u="//2799-129-21-159-89.ngrok.io/"; // Input URL here 
            _paq.push(['setTrackerUrl', u+'matomo.php']);
            _paq.push(['setSiteId', '1']);
            var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
            g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
        })();
        </script>
        <!-- End Matomo Code -->

    </head>
    <body>
        Below is some Client Information gathered using PHP:
        <!-- Some details of the client: IP, Referer Header, User Agent -->
        <?php echo nl2br("\nConnected IP: "), $_SERVER['REMOTE_ADDR']; ?>
        <?php echo nl2br("\nReferer Header: "), $_SERVER['HTTP_REFERER']; ?>
        <?php echo nl2br("\nUser Agent Header: "), $_SERVER['HTTP_USER_AGENT']; ?>

        <!-- Here is client Plugins -->
        <div id="plugins"> </div>

         <!-- Gathering Plugins -->
         <script type="text/javascript">
        var numPlugins = navigator.plugins.length; // num of plugins
        client_plugins = "<br/>List of plugins installed: <br/>"
        if (numPlugins == 0) {
            client_plugins += "None were detected <br/>"
        }
        for(var i=0; i < numPlugins; i++) {
            client_plugins += navigator.plugins[i].name + "<br/>";
        }

        document.getElementById("plugins").innerHTML=client_plugins;
        </script>

    </body>
    
</html>