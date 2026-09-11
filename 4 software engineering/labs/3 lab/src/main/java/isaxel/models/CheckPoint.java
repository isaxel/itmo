package isaxel.models;

import java.io.Serializable;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;


@Data
@Entity
@NoArgsConstructor
@Table(name = "checkpoint")
public class CheckPoint implements Serializable {
    @Id
    @GeneratedValue
    private int id;

    private double x;
    private double y;
    private double r;
    private boolean isInside;
    private Date timestamp;
    private long executionTime;

    public CheckPoint(double x, double y, double r) {
        this.x = x;
        this.y = y;
        this.r = r;
    }

    public void calculate() {
        long now = System.nanoTime();
        isInside = (x <= 0 && y >= 0 && (x * x + y * y <= r * r)) ||
                (x >= 0 && y >= 0 && x <= (r / 2.0) && y <= r) ||
                (x >= 0 && y <= 0 && y >= (x * 2.0 - r));

        timestamp = new Date(System.currentTimeMillis());
        executionTime = System.nanoTime() - now;
    }
    public boolean getIsInside() {
        return isInside;
    }
    public void setIsInside(boolean isInside) {
        this.isInside = isInside;
    }
}
