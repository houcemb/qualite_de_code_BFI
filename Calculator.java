public class Calculator{
    public Calculator(){};
    public float add(float x, float y){
        int i =5;
        int j =5;
        return x+y;

    }
    public float subtract(float x, float y){
        int i =4;
        int j =i;
        return (x-y);

    }
    public float multiply(float x, float y){

        int j =3;
        for (int i =0; i<j; i++){
            String s = new String("x "+i);
        }
        return x*y;

    }
    public  float divide(float x, float y){
        return x/y;
    }
    public int mod(int x, int y){
        return x%y;
    }
}