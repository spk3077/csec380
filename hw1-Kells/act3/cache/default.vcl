vcl 4.0;

backend default {
    .host = "webserver:80";
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 5s;
        .window = 3;
        .threshold = 3;
    }
}

sub vcl_backend_response {
     set beresp.grace = 1h;
}