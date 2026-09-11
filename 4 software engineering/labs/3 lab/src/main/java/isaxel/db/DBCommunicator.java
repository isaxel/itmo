package isaxel.db;

import jakarta.persistence.EntityManager;
import jakarta.persistence.Persistence;
import isaxel.models.CheckPoint;
import isaxel.i18n.Messages;

import java.io.Serializable;
import java.util.ArrayList;

public class DBCommunicator implements Serializable {
    private static volatile DBCommunicator instance;

    public static DBCommunicator getInstance() {
        DBCommunicator localInstance = instance;
        if (localInstance == null) {
            synchronized (DBCommunicator.class) {
                localInstance = instance;
                if (localInstance == null) {
                    instance = localInstance = new DBCommunicator();
                }
            }
        }
        return localInstance;
    }

    private EntityManager manager;

    public DBCommunicator() {
        var managerFactory = Persistence.createEntityManagerFactory(Messages.get("persistence.unit"));
        manager = managerFactory.createEntityManager();
    }

    public void sendOne(CheckPoint point) {
        var transaction = manager.getTransaction();
        try {
            transaction.begin();
            manager.persist(point);
            transaction.commit();
        } catch (Exception e) {
            if (transaction.isActive()) transaction.rollback();
        }
    }

    public ArrayList<CheckPoint> getAll() {
        var transaction = manager.getTransaction();
        try {
            transaction.begin();
            var res = new ArrayList<>(manager.createQuery(Messages.get("query.select.all"), CheckPoint.class).getResultList());
            transaction.commit();
            return res;
        } catch (Exception e) {
            if (transaction.isActive()) transaction.rollback();
            return new ArrayList<>();
        }
    }

    public void clearAll() {
        var transaction = manager.getTransaction();

        transaction.begin();
        manager.createQuery(Messages.get("query.delete.all")).executeUpdate();
        transaction.commit();
    }
}
