import com.fastcgi.FCGIInterface;

import java.util.List;

public class Main {
    private static final double MIN = -5;
    private static final double MAX = 3;
    private static final List<Double> ALLOWED_R = List.of(1.0, 1.5, 2.0, 2.5, 3.0);

    private static final ResultStorage storage = new ResultStorage();

    public static void main(String[] args) {
        FCGIInterface fcgi = new FCGIInterface();
        while (fcgi.FCGIaccept() >= 0) {
            long start = System.nanoTime();
            try {
                handle(Request.read(), start);
            } catch (UnsupportedOperationException e) {
                Response.error(405, e.getMessage());
            } catch (IllegalArgumentException e) {
                Response.error(400, e.getMessage());
            } catch (Exception e) {
                Response.error(500, "Внутренняя ошибка сервера");
                e.printStackTrace(System.err);
            }
        }
    }

    private static void handle(Request req, long start) {
        String action = req.get("action");

        if ("list".equals(action)) {
            Response.ok(storage.getAll());
            return;
        }
        if ("clear".equals(action)) {
            storage.clear();
            Response.ok(storage.getAll());
            return;
        }
        if (action == null) {
            Response.error(400, "Не задано действие");
            return;
        }
        if (!"check".equals(action)) {
            Response.error(400, "Неизвестное действие: " + action);
            return;
        }

        double x = parseCoord("X", req.get("x"));
        double y = parseCoord("Y", req.get("y"));
        double r = parseR(req.get("r"));

        boolean hit = AreaChecker.isHit(x, y, r);

        long executionTime = (System.nanoTime() - start) / 1000;
        storage.add(new Result(x, y, r, hit, System.currentTimeMillis(), executionTime));

        Response.ok(storage.getAll());
    }


    private static double parseCoord(String name, String s) {
        double v = parse(name, s);
        if (!(v > MIN && v < MAX)) {
            throw new IllegalArgumentException(name + " должно быть в интервале (-5 … 3)");
        }
        return v;
    }

    private static double parseR(String s) {
        double r = parse("R", s);
        if (!ALLOWED_R.contains(r)) {
            throw new IllegalArgumentException("R должно быть одним из {1, 1.5, 2, 2.5, 3}");
        }
        return r;
    }

    private static double parse(String name, String s) {
        if (s == null || s.isBlank()) {
            throw new IllegalArgumentException(name + " не задан");
        }
        String n = s.trim().replace(',', '.');
        if (!n.matches("-?\\d{1,12}(\\.\\d{1,14})?")) {
            throw new IllegalArgumentException(name + " должно быть числом");
        }
        return Double.parseDouble(n);
    }
}
