package isaxel.jmx;

import jakarta.servlet.ServletContextEvent;
import jakarta.servlet.ServletContextListener;
import jakarta.servlet.annotation.WebListener;

import javax.management.MBeanServer;
import javax.management.Notification;
import javax.management.NotificationListener;
import javax.management.ObjectName;
import java.lang.management.ManagementFactory;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Регистрирует MBean-ы приложения в платформенном MBeanServer при старте
 * веб-приложения и снимает их с регистрации при остановке (иначе при
 * повторном деплое будет InstanceAlreadyExistsException).
 * <p>
 * Именно эти ObjectName-ы будут видны в JConsole / VisualVM в дереве MBeans
 * в узле «isaxel.jmx».
 */
@WebListener
public class JmxRegistrar implements ServletContextListener, NotificationListener {

    private static final Logger LOG = Logger.getLogger(JmxRegistrar.class.getName());

    public static final String POINT_COUNTER_NAME = "isaxel.jmx:type=PointCounter";
    public static final String AREA_CALCULATOR_NAME = "isaxel.jmx:type=AreaCalculator";

    private ObjectName pointCounterName;
    private ObjectName areaCalculatorName;

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        MBeanServer server = ManagementFactory.getPlatformMBeanServer();
        try {
            pointCounterName = new ObjectName(POINT_COUNTER_NAME);
            areaCalculatorName = new ObjectName(AREA_CALCULATOR_NAME);

            if (!server.isRegistered(pointCounterName)) {
                server.registerMBean(PointCounter.getInstance(), pointCounterName);
            }
            if (!server.isRegistered(areaCalculatorName)) {
                server.registerMBean(AreaCalculator.getInstance(), areaCalculatorName);
            }

            // подписываемся на собственные оповещения, чтобы они были видны
            // в логе сервера, а не только в JConsole
            PointCounter.getInstance().addNotificationListener(this, null, null);

            LOG.info("JMX: MBeans registered -> " + POINT_COUNTER_NAME + ", " + AREA_CALCULATOR_NAME);
        } catch (Exception e) {
            LOG.log(Level.SEVERE, "JMX: не удалось зарегистрировать MBean-ы", e);
        }
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        MBeanServer server = ManagementFactory.getPlatformMBeanServer();
        try {
            PointCounter.getInstance().removeNotificationListener(this);
        } catch (Exception ignored) {
            // слушатель мог быть уже снят
        }
        unregister(server, pointCounterName);
        unregister(server, areaCalculatorName);
        LOG.info("JMX: MBeans unregistered");
    }

    private void unregister(MBeanServer server, ObjectName name) {
        try {
            if (name != null && server.isRegistered(name)) {
                server.unregisterMBean(name);
            }
        } catch (Exception e) {
            LOG.log(Level.WARNING, "JMX: не удалось снять с регистрации " + name, e);
        }
    }

    /** Приём оповещения о серии промахов. */
    @Override
    public void handleNotification(Notification notification, Object handback) {
        LOG.warning("JMX NOTIFICATION [" + notification.getType() + "] #"
                + notification.getSequenceNumber() + ": " + notification.getMessage());
    }
}
