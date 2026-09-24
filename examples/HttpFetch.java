import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

public final class HttpFetch {
    private static final HttpClient CLIENT = HttpClient.newHttpClient();

    /** Fetch the body of a URL as a string. */
    public static String fetch(String url) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url))
                .timeout(Duration.ofSeconds(10))
                .GET()
                .build();
        return CLIENT.send(request, HttpResponse.BodyHandlers.ofString()).body();
    }
}
