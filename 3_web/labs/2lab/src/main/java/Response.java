import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.StringJoiner;

class Response {

    private static final String RESULT_JSON = """
            {
                "ok": true,
                "serverTime": %d,
                "results": [%s]
            }
            """;
    private static final String ROW_JSON = """
            {"x": %s, "y": %s, "r": %s, "hit": %b, "time": %d, "executionTime": %d}""";
    private static final String ERROR_JSON = """
            {
                "ok": false,
                "serverTime": %d,
                "reason": "%s"
            }
            """;
    private static final String HTTP_RESPONSE = """
            HTTP/1.1 %d %s
            Content-Type: application/json; charset=utf-8
            Cache-Control: no-store
            Content-Length: %d

            %s""";

    static void ok(List<Result> results) {
        StringJoiner rows = new StringJoiner(", ");
        for (Result r : results) {
            rows.add(ROW_JSON.formatted(r.x(), r.y(), r.r(), r.hit(), r.time(), r.executionTime()));
        }
        send(200, RESULT_JSON.formatted(System.currentTimeMillis(), rows));
    }

    static void error(int status, String reason) {
        send(status, ERROR_JSON.formatted(System.currentTimeMillis(), escape(reason)));
    }

    private static void send(int status, String json) {
        int length = json.getBytes(StandardCharsets.UTF_8).length;
        byte[] out = HTTP_RESPONSE.formatted(status, reason(status), length, json)
                .getBytes(StandardCharsets.UTF_8);
        System.out.write(out, 0, out.length);
        System.out.flush();
    }

    private static String reason(int status) {
        return switch (status) {
            case 200 -> "OK";
            case 400 -> "Bad Request";
            case 405 -> "Method Not Allowed";
            default -> "Internal Server Error";
        };
    }

    private static String escape(String s) {
        StringBuilder sb = new StringBuilder(s.length());
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"' -> sb.append("\\\"");
                case '\\' -> sb.append("\\\\");
                case '\n' -> sb.append("\\n");
                case '\r' -> sb.append("\\r");
                case '\t' -> sb.append("\\t");
                default -> {
                    if (c < 0x20) {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
                }
            }
        }
        return sb.toString();
    }
}
