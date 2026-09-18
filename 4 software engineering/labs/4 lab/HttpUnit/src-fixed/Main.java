/*
 * Main.java — исправленная версия.
 *
 * Изменения относительно исходной:
 *  1) добавлен вызов HttpUnitOptions.clearScriptErrorMessages() в теле цикла —
 *     он очищает статический список сообщений об ошибках JavaScript
 *     (com.meterware.httpunit.javascript.JavaScript._errorMessages),
 *     который в исходной версии рос неограниченно и был причиной утечки памяти;
 *  2) WebResponse больше не конкатенируется в строку целиком — печатается
 *     только счётчик и код ответа.
 */

import com.meterware.httpunit.GetMethodWebRequest;
import com.meterware.httpunit.HttpUnitOptions;
import com.meterware.httpunit.WebRequest;
import com.meterware.httpunit.WebResponse;
import com.meterware.servletunit.ServletRunner;
import com.meterware.servletunit.ServletUnitClient;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.xml.sax.SAXException;

public class Main {

    public Main() {
    }

    public static void main(String[] args) {
        try {
            HttpUnitOptions.setExceptionsThrownOnScriptError(false);
            ServletRunner sr = new ServletRunner();
            sr.registerServlet("myServlet", HelloWorld.class.getName());
            ServletUnitClient sc = sr.newClient();
            int number = 1;
            WebRequest request = new GetMethodWebRequest("http://test.meterware.com/myServlet");
            while (true) {
                WebResponse response = sc.getResponse(request);

                // ГЛАВНОЕ ИСПРАВЛЕНИЕ: не даём статическому списку расти бесконечно.
                // Если ошибки скриптов нужны для анализа — их следует прочитать
                // через HttpUnitOptions.getScriptErrorMessages() и сразу очистить.
                HttpUnitOptions.clearScriptErrorMessages();

                System.out.println("Count: " + number++ + ", status: " + response.getResponseCode());
                java.lang.Thread.sleep(200);
            }
        } catch (InterruptedException ex) {
            Logger.getLogger("global").log(Level.SEVERE, null, ex);
        } catch (MalformedURLException ex) {
            Logger.getLogger("global").log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger("global").log(Level.SEVERE, null, ex);
        } catch (SAXException ex) {
            Logger.getLogger("global").log(Level.SEVERE, null, ex);
        }
    }
}
