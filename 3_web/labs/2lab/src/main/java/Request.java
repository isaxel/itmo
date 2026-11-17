import com.fastcgi.FCGIInterface;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;


class Request {
    private static final int MAX_BODY = 4096;

    private final Map<String, String> form;
    private final String method;

    private Request(String method, Map<String, String> form) {
        this.form = form;
        this.method = method;
    }

    static Request read() throws IOException {
        Properties params = FCGIInterface.request.params;
        String method = params.getProperty("REQUEST_METHOD", "");
        if (!("POST".equals(method)) && !("DELETE".equals(method))) {
            throw new UnsupportedOperationException("Метод " + method + " не поддерживается, используйте POST");
        }
        return new Request(method, parseForm((readBody(params))));
    }

    String get(String name) {
        return form.get(name);
    }

    String getMethod() {
        return method;
    }

    private static String readBody(Properties params) throws IOException {
        String lenStr = params.getProperty("CONTENT_LENGTH", "0").trim();
        int len;
        try {
            len = lenStr.isEmpty() ? 0 : Integer.parseInt(lenStr);
        } catch (NumberFormatException e) {
            throw new IllegalArgumentException("Некорректный CONTENT_LENGTH");
        }
        if (len < 0 || len > MAX_BODY) {
            throw new IllegalArgumentException("Слишком большое тело запроса");
        }
        InputStream in = System.in;
        ByteArrayOutputStream buf = new ByteArrayOutputStream(len);
        byte[] chunk = new byte[512];
        int remaining = len;
        while (remaining > 0) {
            int n = in.read(chunk, 0, Math.min(chunk.length, remaining));
            if (n < 0) break;
            buf.write(chunk, 0, n);
            remaining -= n;
        }
        return buf.toString(StandardCharsets.UTF_8);
    }

    private static Map<String, String> parseForm(String body) {
        Map<String, String> map = new HashMap<>();
        for (String pair : body.split("&")) {
            if (pair.isEmpty()) continue;
            int i = pair.indexOf('=');
            try {
                String k = URLDecoder.decode(i < 0 ? pair : pair.substring(0, i), StandardCharsets.UTF_8);
                String v = i < 0 ? "" : URLDecoder.decode(pair.substring(i + 1), StandardCharsets.UTF_8);
                map.put(k, v);
            } catch (IllegalArgumentException e) {
                throw new IllegalArgumentException("Некорректное тело запроса");
            }
        }
        return map;
    }
}
