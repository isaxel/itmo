package isaxel.jmx;

import javax.management.MBeanNotificationInfo;
import javax.management.Notification;
import javax.management.NotificationBroadcasterSupport;
import java.util.concurrent.atomic.AtomicLong;

/**
 * MBean, считающий общее число установленных пользователем точек и число
 * промахов (точек, не попавших в область).
 * <p>
 * Наследование от {@link NotificationBroadcasterSupport} даёт готовую
 * реализацию NotificationEmitter: MBean может рассылать оповещения
 * подписчикам (JConsole, VisualVM, собственный NotificationListener).
 * Если пользователь совершил 2 промаха подряд — рассылается оповещение
 * типа {@link #MISS_STREAK_NOTIFICATION}.
 */
public class PointCounter extends NotificationBroadcasterSupport implements PointCounterMBean {

    /** Тип рассылаемого оповещения. */
    public static final String MISS_STREAK_NOTIFICATION = "isaxel.point.missStreak";

    /** Сколько промахов подряд считается поводом для оповещения. */
    public static final int MISS_STREAK_THRESHOLD = 2;

    private static final PointCounter INSTANCE = new PointCounter();

    public static PointCounter getInstance() {
        return INSTANCE;
    }

    private final AtomicLong sequenceNumber = new AtomicLong(1);

    private long totalPoints;
    private long missedPoints;
    private int consecutiveMisses;
    private long notificationsSent;

    private PointCounter() {
    }

    /**
     * Вызывается из бина приложения после проверки очередной точки.
     *
     * @param inside true, если точка попала в область
     */
    public synchronized void registerPoint(double x, double y, double r, boolean inside) {
        totalPoints++;
        if (inside) {
            consecutiveMisses = 0;
            return;
        }

        missedPoints++;
        consecutiveMisses++;

        if (consecutiveMisses >= MISS_STREAK_THRESHOLD) {
            notificationsSent++;
            String message = String.format(
                    "Пользователь совершил %d промаха(ов) подряд. Последняя точка: x=%s, y=%s, r=%s",
                    consecutiveMisses, x, y, r);
            Notification notification = new Notification(
                    MISS_STREAK_NOTIFICATION,
                    this,
                    sequenceNumber.getAndIncrement(),
                    System.currentTimeMillis(),
                    message);
            notification.setUserData(consecutiveMisses);
            // рассылка всем подписчикам (в т.ч. JConsole / VisualVM)
            sendNotification(notification);
        }
    }

    @Override
    public synchronized long getTotalPoints() {
        return totalPoints;
    }

    @Override
    public synchronized long getMissedPoints() {
        return missedPoints;
    }

    @Override
    public synchronized long getHitPoints() {
        return totalPoints - missedPoints;
    }

    @Override
    public synchronized double getMissRate() {
        if (totalPoints == 0) {
            return 0.0;
        }
        return Math.round(missedPoints * 100_000.0 / totalPoints) / 1000.0;
    }

    @Override
    public synchronized int getConsecutiveMisses() {
        return consecutiveMisses;
    }

    @Override
    public synchronized long getNotificationsSent() {
        return notificationsSent;
    }

    @Override
    public synchronized void reset() {
        totalPoints = 0;
        missedPoints = 0;
        consecutiveMisses = 0;
        notificationsSent = 0;
    }

    /**
     * Описание рассылаемых оповещений — именно его показывает JConsole
     * на вкладке Notifications данного MBean-а.
     */
    @Override
    public MBeanNotificationInfo[] getNotificationInfo() {
        return new MBeanNotificationInfo[]{
                new MBeanNotificationInfo(
                        new String[]{MISS_STREAK_NOTIFICATION},
                        Notification.class.getName(),
                        "Оповещение о " + MISS_STREAK_THRESHOLD + " и более промахах подряд")
        };
    }
}
