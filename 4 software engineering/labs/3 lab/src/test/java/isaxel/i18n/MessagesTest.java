package isaxel.i18n;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Locale;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class MessagesTest {
    private static final Locale RU = Locale.forLanguageTag("ru");

    @Test
    @DisplayName("Значения по умолчанию читаются из messages.properties")
    void defaultBundleIsLoaded() {
        assertTrue(Messages.get(Locale.ENGLISH, "app.result.inside").contains("INSIDE"));
    }

    @Test
    @DisplayName("Русская локаль читается из messages_ru.properties")
    void russianBundleIsLoaded() {
        String ru = Messages.get(RU, "app.title");
        assertTrue(ru.contains("лабораторная"), "ожидался русский текст, получено: " + ru);
        assertNotEquals(Messages.get(Locale.ENGLISH, "app.title"), ru);
    }

    @Test
    @DisplayName("Отсутствующие в ru-файле ключи наследуются из файла по умолчанию")
    void technicalKeysAreInherited() {
        assertEquals("default", Messages.get(RU, "persistence.unit"));
        assertEquals("update", Messages.get(RU, "nav.outcome.update"));
        assertEquals("reset", Messages.get(RU, "nav.outcome.reset"));
    }

    @Test
    @DisplayName("Подстановка параметров в локализованную строку")
    void formatSubstitutesArguments() {
        Locale previous = Locale.getDefault();
        try {
            Messages.setLocale(Locale.ENGLISH);
            String message = Messages.format("app.input", 1, 2, 3);
            assertTrue(message.contains("x=1"), message);
            assertTrue(message.contains("y=2"), message);
            assertTrue(message.contains("r=3"), message);
        } finally {
            Messages.setLocale(previous);
        }
    }
}
