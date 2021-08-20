package com.github.h4iku;

public class App {
    public static void main(String[] args) throws Exception {

        String filePath1 = "resources/AssertionTask.java";
        String result1 = "void assertOnIndex(int index);";
        Line line1 = Test.checkLine(filePath1, 24).get();
        System.out.println(line1);
        if (!line1.getContent().trim().equals(result1))
            System.out.println("Nope");

        String filePath2 = "resources/LocalizedMessage.java";
        String result2 = "public class LocalizedMessage implements Comparable {";
        Line line2 = Test.checkLine(filePath2, 25).get();
        System.out.println(line2);
        if (!line2.getContent().trim().equals(result2))
            System.out.println("Nope");

        String filePath3 = "resources/RolesTest.java";
        String result3 = "String result = engine.execute( query ) .dumpToString();";
        Test.checkLine(filePath3, 194);
        // Line line3 = Test.checkLine(filePath3, 194).get();
        // System.out.println(line3);
        // if (!line3.getContent().trim().equals(result3))
        // System.out.println("Nope");

        String filePath4 = "resources/XdocsPagesTest.java";
        String result4 = "if (\"Notes\".equals(subSectionName) || \"Rule Description\".equals(subSectionName) || \"Metadata\".equals(subSectionName)) {;";
        Test.checkLine(filePath4, 1102);

    }
}
