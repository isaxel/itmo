import java.util.ArrayList;
import java.util.List;


class ResultStorage {
    private static final int MAX_ROWS = 1000;

    private final List<Result> results = new ArrayList<>();

    void add(Result r) {
        results.add(r);
        if (results.size() > MAX_ROWS) {
            results.remove(0);
        }
    }

    List<Result> getAll() {
        return List.copyOf(results);
    }

    void clear() {
        results.clear();
    }
}
