class AreaChecker {
    static boolean isHit(double x, double y, double r) {
        double half = r / 2;

        if (x >= 0 && y >= 0) {
            return x <= r && y <= half;
        }
        if (x <= 0 && y >= 0) {
            return y <= x + half;
        }
        if (x <= 0 && y <= 0) {
            return x * x + y * y <= half * half;
        }
        return false;
    }
}
