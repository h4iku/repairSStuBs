package com.github.h4iku;

import com.github.h4iku.Test;
import com.github.h4iku.Line;

public class App {
    public static void main(String[] args) throws Exception {

        String filePath1 = "resources/AssertionTask.java";
        String result1 = "void assertOnIndex(int index);";
        Line line1 = Test.checkLine(filePath1, 24).get();
        System.out.println(line1);
        // if (!line.getLine().trim().equals(result1))
        // System.out.println("Nope");

        String filePath2 = "resources/LocalizedMessage.java";
        String result2 = "public class LocalizedMessage implements Comparable {";
        Line line2 = Test.checkLine(filePath2, 25).get();
        System.out.println(line1);

    }
}
