package isaxel.jmx;

/**
 * Интерфейс стандартного MBean-а, определяющего площадь получившейся фигуры.
 */
public interface AreaCalculatorMBean {

    /** Текущий радиус R, по которому построена фигура. */
    double getR();

    /** R можно поменять прямо из JConsole (атрибут доступен на запись). */
    void setR(double r);

    /** Площадь четверти круга (II четверть): PI * R^2 / 4. */
    double getSectorArea();

    /** Площадь прямоугольника (I четверть): R/2 * R. */
    double getRectangleArea();

    /** Площадь треугольника (IV четверть): 1/2 * R/2 * R. */
    double getTriangleArea();

    /** Полная площадь фигуры. */
    double getTotalArea();

    /** Операция: посчитать площадь для произвольного R, не меняя текущий. */
    double areaForRadius(double radius);
}
