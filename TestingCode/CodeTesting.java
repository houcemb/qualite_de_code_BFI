public class CodeTesting {

    public int addNumbers(int a, int b) {
        return a + b;
    }

    public int addValues(int x, int y) {
        return x + y;
    }

    public int Test(int x, int y) {
        return x * y;
    }

    public String greet(String name) {
        return "Hello, " + name;
    }

    public String welcome(String name) {
        return "Welcome, " + name;
    }

    public void printNumbers() {
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
        }
    }

    public void displayNumbers() {
        int array_a[];
        int array_b[];

        int sum_a = 0;

        for (int i = 0; i < 4; i++)
            sum_a += array_a[i];

        int average_a = sum_a / 4;

        int sum_b = 0;

        for (int i = 0; i < 4; i++)
            sum_b += array_b[i];

        int average_b = sum_b / 4;

        for (int i = 0; i < 4; i++) {
            String s = new String("test");

        }
        int k = 0;

        while (true) {
            k++;
            String s = new String("test");
            if (k == 4) {
                break;
            }

        }
        synchronized (this) {
        k = 0;}

        do {
            k++;

            String s = new String("test");
        } while (k <= 4);
    }
    public void GoForRun()
    {
        GetDressed();
        Run();
        Shower();
    }

  synchronized   public void LiftWeights()
    {

        GetDressed();
        Lift();
        Shower();
    }

}
class test{

}
