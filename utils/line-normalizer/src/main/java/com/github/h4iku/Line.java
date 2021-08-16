package com.github.h4iku;

public class Line {
    private String content;
    private int begin;
    private int end;

    public Line(String line, int begin, int end) {
        this.content = line;
        this.begin = begin;
        this.end = end;
    }

    public Line() {
    }

    public String getContent() {
        return content;
    }

    public void setContent(String line) {
        this.content = line;
    }

    public int getBegin() {
        return begin;
    }

    public void setBegin(int begin) {
        this.begin = begin;
    }

    public int getEnd() {
        return end;
    }

    public void setEnd(int end) {
        this.end = end;
    }

    @Override
    public String toString() {
        return "Line [begin=" + begin + ", end=" + end + ", content=" + content + "]";
    }

}
