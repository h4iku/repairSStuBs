package com.github.h4iku;

import com.github.h4iku.Test;
import com.github.h4iku.Line;

public class App {
    public static void main(String[] args) throws Exception {

        String filePath1 = "resources/AssertionTask.java";
        String result1 = "void assertOnIndex(int index);";
        Line line = Test.checkLine(filePath1, 25).get();
        // System.out.println(line);
        // if (!line.getLine().trim().equals(result1))
        // System.out.println("Nope");

    }
}
