package isaxel.jmx;

/**
 * Интерфейс стандартного MBean-а, считающего точки, установленные пользователем.
 * Имя интерфейса обязано быть вида &lt;ИмяКласса&gt;MBean — иначе JMX не увидит
 * в классе PointCounter стандартный MBean.
 */
public interface PointCounterMBean {

    /** Общее число установленных пользователем точек. */
    long getTotalPoints();

    /** Число точек, НЕ попавших в область. */
    long getMissedPoints();

    /** Число точек, попавших в область. */
    long getHitPoints();

    /** Доля промахов, % */
    double getMissRate();

    /** Длина текущей серии промахов подряд. */
    int getConsecutiveMisses();

    /** Сколько раз уже отправлялось оповещение о двух промахах подряд. */
    long getNotificationsSent();

    /** Операция: обнулить статистику (видна в JConsole на вкладке Operations). */
    void reset();
}
