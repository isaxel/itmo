package isaxel;

import isaxel.i18n.Messages;
import isaxel.models.CheckPoint;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Locale;

import static org.junit.jupiter.api.Assertions.assertTrue;

class MainTest {
    @AfterEach
    void restoreLocale() {
        Messages.setLocale(Locale.getDefault());
    }

    @Test
    @DisplayName("Описание результата для точки внутри области")
    void describeInsidePoint() {
        Messages.setLocale(Locale.ENGLISH);
        String result = Main.describe(new CheckPoint(1, 2, 3));
        assertTrue(result.contains("INSIDE"), result);
        assertTrue(result.contains("Calculation time"), result);
    }

    @Test
    @DisplayName("Описание результата для точки вне области")
    void describeOutsidePoint() {
        Messages.setLocale(Locale.ENGLISH);
        String result = Main.describe(new CheckPoint(2, 2, 3));
        assertTrue(result.contains("OUTSIDE"), result);
    }

    @Test
    @DisplayName("Русская локаль подставляется в результат")
    void describeInRussian() {
        Messages.setLocale(Locale.forLanguageTag("ru"));
        String result = Main.describe(new CheckPoint(1, 2, 3));
        assertTrue(result.contains("попадает"), result);
    }
}
