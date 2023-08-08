package com.rule;
import net.sourceforge.pmd.lang.java.ast.*;
import net.sourceforge.pmd.lang.java.rule.AbstractIgnoredAnnotationRule;

public class Rule extends AbstractIgnoredAnnotationRule {

    public Rule() {
            addRuleChainVisit(ASTClassOrInterfaceDeclaration.class);
        }

    @Override
    public Object visit(ASTConstructorCall node, Object data) {


        if (constructorInForLoop(node)) {
            addViolation(data, node);
        }

        return super.visit(node, data);
    }

    private boolean constructorInForLoop(ASTConstructorCall node) {
        return node.ancestors().toStream()
                .anyMatch(ancestor -> ancestor instanceof ASTForStatement);
    }
}
