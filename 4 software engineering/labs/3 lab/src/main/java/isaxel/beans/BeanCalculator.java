package isaxel.beans;

import jakarta.annotation.PostConstruct;
import jakarta.enterprise.context.SessionScoped;
import jakarta.inject.Named;
import lombok.Getter;
import lombok.Setter;
import isaxel.models.CheckPoint;
import isaxel.db.DBCommunicator;
import isaxel.i18n.Messages;

import java.io.Serializable;
import java.util.ArrayList;

@Named("beanCalculator")
@SessionScoped
public class BeanCalculator implements Serializable {
    @Getter
    private double x;
    @Getter
    private double y;
    @Setter
    @Getter
    private double r;

    @Setter
    @Getter
    private ArrayList<CheckPoint> bigList;
    private DBCommunicator dbCommunicator;

    @PostConstruct
    public void init() {
        x = 0;
        y = 0;
        r = 3;
        dbCommunicator = DBCommunicator.getInstance();
        bigList = dbCommunicator.getAll();
        if (bigList == null) {
            bigList = new ArrayList<>();
        }
    }

    public String reset() {
        dbCommunicator.clearAll();
        bigList.clear();
        return Messages.get("nav.outcome.reset");
    }

    public String calc() {
        var point = new CheckPoint(x, y, r);
        point.calculate();
        bigList.add(point);
        dbCommunicator.sendOne(point);
        return Messages.get("nav.outcome.update");
    }

    public void setX(double x) {
        this.x = ((Long) Math.round(x * 1000)).doubleValue() / 1000;
    }

    public void setY(double y) {
        this.y = ((Long) Math.round(y * 1000)).doubleValue() / 1000;
    }
}
