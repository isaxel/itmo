package isaxel;

import isaxel.i18n.Messages;
import isaxel.models.CheckPoint;

public final class Main {
    private static final double DEFAULT_X = 0;
    private static final double DEFAULT_Y = 0;
    private static final double DEFAULT_R = 3;

    private Main() {
    }

    public static void main(String[] args) {
        System.out.println(Messages.get("app.title"));

        double x = DEFAULT_X;
        double y = DEFAULT_Y;
        double r = DEFAULT_R;

        if (args.length >= 3) {
            x = parse(args[0], DEFAULT_X);
            y = parse(args[1], DEFAULT_Y);
            r = parse(args[2], DEFAULT_R);
        } else {
            System.out.println(Messages.get("app.usage"));
        }

        System.out.println(Messages.format("app.input", x, y, r));
        System.out.println(describe(new CheckPoint(x, y, r)));
    }

    public static String describe(CheckPoint point) {
        point.calculate();
        String key = point.getIsInside() ? "app.result.inside" : "app.result.outside";
        return Messages.format(key, point.getX(), point.getY(), point.getR())
                + System.lineSeparator()
                + Messages.format("app.result.time", point.getExecutionTime());
    }

    private static double parse(String value, double fallback) {
        try {
            return Double.parseDouble(value);
        } catch (NumberFormatException e) {
            System.out.println(Messages.format("app.error.number", value));
            return fallback;
        }
    }
}
