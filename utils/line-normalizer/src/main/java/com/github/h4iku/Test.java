package com.github.h4iku;

import java.io.File;
import java.util.List;
import java.util.Optional;

import com.github.javaparser.JavaToken;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.TokenRange;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.comments.JavadocComment;

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

            if (comment.getRange().get().begin.line < lineNumber && comment.getRange().get().end.line > lineNumber) {
                // When the line is in the middle of comments, ignore it.
                return Optional.empty();

            } else if (comment.getRange().get().begin.line == lineNumber && (comment instanceof JavadocComment)
                    && comment.getCommentedNode().isPresent()) {
                // For line numbers pointing at the beginning of a Javadoc
                Node node = comment.getCommentedNode().get();
                return Optional.of(handleCommentedNode(node));
            }
        }

        return Optional.empty();

    }

    private static Line handleCommentedNode(Node node) {
        MethodDeclaration md = node.findFirst(MethodDeclaration.class).get();
        Line line = new Line();
        line.setBegin(md.getRange().get().begin.line);

        for (JavaToken jToken : md.getTokenRange().get()) {
            if (jToken.getText().equals("{")) {
                line.setEnd(jToken.getRange().get().end.line);
                line.setContent(md.getDeclarationAsString() + " {");
                break;
            } else if (jToken.getText().equals(";")) {
                line.setEnd(jToken.getRange().get().end.line);
                line.setContent(md.getDeclarationAsString() + ";");
                break;
            }
        }

        System.out.println(line);

        // md.getTokenRange().get().forEach(token -> {
        // System.out.println(token);
        // });
        // Line line = new Line(md.getDeclarationAsString(),
        // md.getRange().get().begin.line,
        // md.getRange().get().begin.line);
        return line;
    }

}
