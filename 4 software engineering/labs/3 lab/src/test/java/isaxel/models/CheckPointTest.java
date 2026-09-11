package isaxel.models;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CheckPointTest {
    @Test
    @DisplayName("Точка (0;0) принадлежит области при любом R")
    void originIsInside() {
        CheckPoint point = new CheckPoint(0, 0, 3);
        point.calculate();
        assertTrue(point.getIsInside());
    }

    @ParameterizedTest(name = "({0}; {1}), R={2} -> внутри")
    @CsvSource({
            "-1,   1,   3",
            "-2,   2,   3",
            "1,    2,   3",
            "1.5,  3,   3",
            "0.5, -1,   3",
            "0,   -3,   3"
    })
    void pointsInsideArea(double x, double y, double r) {
        CheckPoint point = new CheckPoint(x, y, r);
        point.calculate();
        assertTrue(point.getIsInside(), "ожидалось попадание в область");
    }

    @ParameterizedTest(name = "({0}; {1}), R={2} -> снаружи")
    @CsvSource({
            "-3,   3,   3",
            "2,    2,   3",
            "2,   -1,   3",
            "-1,  -1,   3",
            "1.6,  3,   3"
    })
    void pointsOutsideArea(double x, double y, double r) {
        CheckPoint point = new CheckPoint(x, y, r);
        point.calculate();
        assertFalse(point.getIsInside(), "ожидалось непопадание в область");
    }

    @Test
    @DisplayName("calculate() проставляет время и метку времени")
    void calculateFillsMetadata() {
        CheckPoint point = new CheckPoint(1, 1, 2);
        point.calculate();
        assertNotNull(point.getTimestamp());
        assertTrue(point.getExecutionTime() > 0, "время выполнения должно быть положительным");
    }

    @Test
    @DisplayName("Конструктор сохраняет параметры точки")
    void constructorKeepsArguments() {
        CheckPoint point = new CheckPoint(1.5, -2.5, 2);
        assertEquals(1.5, point.getX());
        assertEquals(-2.5, point.getY());
        assertEquals(2, point.getR());
    }
}
