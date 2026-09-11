package isaxel.i18n;

import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;

public final class Messages {
    public static final String BUNDLE_NAME = "i18n.messages";

    private static volatile ResourceBundle bundle = ResourceBundle.getBundle(BUNDLE_NAME);

    private Messages() {
    }

    public static void setLocale(Locale locale) {
        bundle = ResourceBundle.getBundle(BUNDLE_NAME, locale);
    }

    public static ResourceBundle getBundle() {
        return bundle;
    }

    public static String get(String key) {
        return bundle.getString(key);
    }

    public static String get(Locale locale, String key) {
        return ResourceBundle.getBundle(BUNDLE_NAME, locale).getString(key);
    }

    public static String format(String key, Object... args) {
        return new MessageFormat(get(key), Locale.ROOT).format(args);
    }
}
