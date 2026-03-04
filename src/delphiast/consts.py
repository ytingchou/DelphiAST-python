"""Constants and enum mappings mirrored from DelphiAST.Consts.pas."""

from __future__ import annotations

from enum import IntEnum


class TSyntaxNodeType(IntEnum):
    ntUnknown = 0
    ntAbsolute = 1
    ntAdd = 2
    ntAddr = 3
    ntAlignmentParam = 4
    ntAnd = 5
    ntAnonymousMethod = 6
    ntArguments = 7
    ntAs = 8
    ntAssign = 9
    ntAt = 10
    ntAttribute = 11
    ntAttributes = 12
    ntBounds = 13
    ntCall = 14
    ntCase = 15
    ntCaseElse = 16
    ntCaseLabel = 17
    ntCaseLabels = 18
    ntCaseSelector = 19
    ntClassConstraint = 20
    ntConstant = 21
    ntConstants = 22
    ntConstraints = 23
    ntConstructorConstraint = 24
    ntContains = 25
    ntDefault = 26
    ntDeref = 27
    ntDimension = 28
    ntDiv = 29
    ntDot = 30
    ntDownTo = 31
    ntElement = 32
    ntElse = 33
    ntEmptyStatement = 34
    ntEnum = 35
    ntEqual = 36
    ntExcept = 37
    ntExceptionHandler = 38
    ntExports = 39
    ntExpression = 40
    ntExpressions = 41
    ntExternal = 42
    ntFDiv = 43
    ntField = 44
    ntFields = 45
    ntFinalization = 46
    ntFinally = 47
    ntFor = 48
    ntFrom = 49
    ntGeneric = 50
    ntGoto = 51
    ntGreater = 52
    ntGreaterEqual = 53
    ntGuid = 54
    ntHelper = 55
    ntIdentifier = 56
    ntIf = 57
    ntImplementation = 58
    ntImplements = 59
    ntIn = 60
    ntIndex = 61
    ntIndexed = 62
    ntInherited = 63
    ntInitialization = 64
    ntInterface = 65
    ntIs = 66
    ntIsNot = 67
    ntLabel = 68
    ntLHS = 69
    ntLiteral = 70
    ntLower = 71
    ntLowerEqual = 72
    ntMessage = 73
    ntMethod = 74
    ntMod = 75
    ntMul = 76
    ntName = 77
    ntNamedArgument = 78
    ntNotEqual = 79
    ntNot = 80
    ntNotIn = 81
    ntOr = 82
    ntPackage = 83
    ntParameter = 84
    ntParameters = 85
    ntPath = 86
    ntPositionalArgument = 87
    ntProtected = 88
    ntPrivate = 89
    ntProperty = 90
    ntPublic = 91
    ntPublished = 92
    ntRaise = 93
    ntRead = 94
    ntRecordConstraint = 95
    ntRepeat = 96
    ntRequires = 97
    ntResolutionClause = 98
    ntResourceString = 99
    ntReturnType = 100
    ntRHS = 101
    ntRoundClose = 102
    ntRoundOpen = 103
    ntSet = 104
    ntShl = 105
    ntShr = 106
    ntStatement = 107
    ntStatements = 108
    ntStrictPrivate = 109
    ntStrictProtected = 110
    ntSub = 111
    ntSubrange = 112
    ntTernaryOp = 113
    ntThen = 114
    ntTo = 115
    ntTry = 116
    ntType = 117
    ntTypeArgs = 118
    ntTypeDecl = 119
    ntTypeParam = 120
    ntTypeParams = 121
    ntTypeSection = 122
    ntValue = 123
    ntVariable = 124
    ntVariables = 125
    ntXor = 126
    ntUnaryMinus = 127
    ntUnit = 128
    ntUses = 129
    ntWhile = 130
    ntWith = 131
    ntWrite = 132
    ntAnsiComment = 133
    ntBorComment = 134
    ntSlashesComment = 135


class TAttributeName(IntEnum):
    anType = 0
    anClass = 1
    anForwarded = 2
    anKind = 3
    anName = 4
    anVisibility = 5
    anCallingConvention = 6
    anPath = 7
    anMethodBinding = 8
    anReintroduce = 9
    anOverload = 10
    anAbstract = 11
    anInline = 12
    anAlign = 13

SYNTAX_NODE_NAMES: tuple[str, ...] = ('unknown', 'absolute', 'add', 'addr', 'alignmentparam', 'and', 'anonymousmethod', 'arguments', 'as', 'assign', 'at', 'attribute', 'attributes', 'bounds', 'call', 'case', 'caseelse', 'caselabel', 'caselabels', 'caseselector', 'classconstraint', 'constant', 'constants', 'constraints', 'constructorconstraint', 'contains', 'default', 'deref', 'dimension', 'div', 'dot', 'downto', 'element', 'else', 'emptystatement', 'enum', 'equal', 'except', 'exceptionhandler', 'exports', 'expression', 'expressions', 'external', 'fdiv', 'field', 'fields', 'finalization', 'finally', 'for', 'from', 'generic', 'goto', 'greater', 'greaterequal', 'guid', 'helper', 'identifier', 'if', 'implementation', 'implements', 'in', 'index', 'indexed', 'inherited', 'initialization', 'interface', 'is', 'isnot', 'label', 'lhs', 'literal', 'lower', 'lowerequal', 'message', 'method', 'mod', 'mul', 'name', 'namedargument', 'notequal', 'not', 'notin', 'or', 'package', 'parameter', 'parameters', 'path', 'positionalargument', 'protected', 'private', 'property', 'public', 'published', 'raise', 'read', 'recordconstraint', 'repeat', 'requires', 'resolutionclause', 'resourcestring', 'returntype', 'rhs', 'roundclose', 'roundopen', 'set', 'shl', 'shr', 'statement', 'statements', 'strictprivate', 'strictprotected', 'sub', 'subrange', 'ternaryop', 'then', 'to', 'try', 'type', 'typeargs', 'typedecl', 'typeparam', 'typeparams', 'typesection', 'value', 'variable', 'variables', 'xor', 'unaryminus', 'unit', 'uses', 'while', 'with', 'write', 'ansicomment', 'borlandcomment', 'slashescomment',)
ATTRIBUTE_NAME_STRINGS: tuple[str, ...] = ('type', 'class', 'forwarded', 'kind', 'name', 'visibility', 'callingconvention', 'path', 'methodbinding', 'reintroduce', 'overload', 'abstract', 'inline', 'align',)

SYNTAX_NODE_TYPE_BY_NAME: dict[str, TSyntaxNodeType] = {
    name: TSyntaxNodeType(index) for index, name in enumerate(SYNTAX_NODE_NAMES)
}
ATTRIBUTE_NAME_BY_STRING: dict[str, TAttributeName] = {
    name: TAttributeName(index) for index, name in enumerate(ATTRIBUTE_NAME_STRINGS)
}


def syntax_node_name(node_type: TSyntaxNodeType) -> str:
    return SYNTAX_NODE_NAMES[int(node_type)]


def attribute_name(attr: TAttributeName) -> str:
    return ATTRIBUTE_NAME_STRINGS[int(attr)]

