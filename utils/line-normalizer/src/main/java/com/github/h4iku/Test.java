package com.github.h4iku;

import java.io.File;
import java.util.List;
import java.util.Optional;

import com.github.javaparser.JavaToken;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.TokenRange;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import com.github.javaparser.ast.visitor.GenericVisitor;
import com.github.javaparser.ast.visitor.GenericVisitorAdapter;
import com.github.javaparser.ast.visitor.VoidVisitor;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class Test {

    public static Optional<Line> checkLine(String srcFile, int lineNumber) throws Exception {

        CompilationUnit cu = StaticJavaParser.parse(new File(srcFile));

        // Check class line range
        if (!(cu.getRange().get().begin.line <= lineNumber && lineNumber <= cu.getRange().get().end.line)) {
            return Optional.empty();
        }

        // Check for lines pointing at comments
        List<Comment> comments = cu.getAllContainedComments();
        for (Comment comment : comments) {

            // When the line is in the middle of comments
            if (comment.getRange().get().begin.line <= lineNumber && comment.getRange().get().end.line >= lineNumber) {

                // For line numbers pointing at the beginning of a Javadoc
                if (comment.getRange().get().begin.line == lineNumber && (comment instanceof JavadocComment)
                        && comment.getCommentedNode().isPresent()) {
                    Node node = comment.getCommentedNode().get();
                    if (node instanceof MethodDeclaration) {
                        Line line = handleCommentedNode((MethodDeclaration) node);
                        return Optional.of(line);
                    } else if (node instanceof ClassOrInterfaceDeclaration) {
                        Line line = handleCommentedNode((ClassOrInterfaceDeclaration) node);
                        return Optional.of(line);
                    } else {
                        System.out.println("Not handled yet");
                    }
                } else {
                    return Optional.empty();
                }
            }
        }

        List<MethodDeclaration> mds = cu.findAll(MethodDeclaration.class);
        for (MethodDeclaration md : mds) {
            if (md.getRange().get().begin.line <= lineNumber && lineNumber <= md.getRange().get().end.line) {
                VoidVisitor<Void> lineExtractor = new LineExtractor(lineNumber);
                lineExtractor.visit(md, null);
            }
        }

        return Optional.empty();

    }

    private static Line handleCommentedNode(MethodDeclaration node) {

        MethodDeclaration md = node.findFirst(MethodDeclaration.class).get();
        Line line = new Line();
        line.setBegin(md.getRange().get().begin.line);

        for (JavaToken jToken : md.getTokenRange().get()) {
            if (jToken.getCategory().isSeparator() && jToken.getText().equals("{")) {
                line.setEnd(jToken.getRange().get().end.line);
                line.setContent(md.getDeclarationAsString() + " {");
                break;
            } else if (jToken.getCategory().isSeparator() && jToken.getText().equals(";")) {
                line.setEnd(jToken.getRange().get().end.line);
                line.setContent(md.getDeclarationAsString() + ";");
                break;
            }
        }

        return line;
    }

    private static Line handleCommentedNode(ClassOrInterfaceDeclaration node) {

        ClassOrInterfaceDeclaration coid = node.findFirst(ClassOrInterfaceDeclaration.class).get();
        Line line = new Line();
        line.setBegin(coid.getRange().get().begin.line);

        String content = "";
        for (JavaToken jToken : coid.getTokenRange().get()) {
            if (jToken.getCategory().isSeparator() && jToken.getText().equals("{")) {
                line.setEnd(jToken.getRange().get().end.line);
                line.setContent(content.replaceAll("\\s+", " ") + "{");
                break;
            } else if (!jToken.getCategory().isComment()) {
                content += jToken.getText();
            }
        }

        return line;
    }

    public static class LineExtractor extends VoidVisitorAdapter<Void> {

        private int lineNumber;

        public LineExtractor(int lineNumber) {
            this.lineNumber = lineNumber;
        }

        @Override
        public void visit(VariableDeclarationExpr vde, Void arg) {
            super.visit(vde, arg);

            // TODO: Write a method for this repetitive line number inclusion test.
            if (vde.getRange().get().begin.line <= lineNumber && lineNumber <= vde.getRange().get().end.line) {
                System.out.println(vde);
            }
            // Line line = new Line();

        }

    }

}
