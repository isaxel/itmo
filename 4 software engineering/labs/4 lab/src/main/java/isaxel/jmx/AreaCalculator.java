package isaxel.jmx;

/**
 * MBean, определяющий площадь получившейся фигуры.
 * <p>
 * Фигура из лабораторной №3 состоит из трёх частей:
 * <ul>
 *   <li>II четверть — четверть круга радиуса R:  S = PI * R^2 / 4;</li>
 *   <li>I  четверть — прямоугольник R/2 x R:     S = R^2 / 2;</li>
 *   <li>IV четверть — треугольник с катетами R/2 и R: S = R^2 / 4.</li>
 * </ul>
 * Итого: S = R^2 * (PI + 3) / 4.
 */
public class AreaCalculator implements AreaCalculatorMBean {

    private static final AreaCalculator INSTANCE = new AreaCalculator();

    public static AreaCalculator getInstance() {
        return INSTANCE;
    }

    /** Радиус по умолчанию совпадает со значением в BeanCalculator.init(). */
    private volatile double r = 3.0;

    private AreaCalculator() {
    }

    @Override
    public double getR() {
        return r;
    }

    @Override
    public void setR(double r) {
        this.r = r;
    }

    @Override
    public double getSectorArea() {
        return round(Math.PI * r * r / 4.0);
    }

    @Override
    public double getRectangleArea() {
        return round(r * r / 2.0);
    }

    @Override
    public double getTriangleArea() {
        return round(r * r / 4.0);
    }

    @Override
    public double getTotalArea() {
        return round(areaForRadius(r));
    }

    @Override
    public double areaForRadius(double radius) {
        return round(radius * radius * (Math.PI + 3.0) / 4.0);
    }

    private static double round(double value) {
        return Math.round(value * 1000.0) / 1000.0;
    }
}
