"""Selector is a single Selector of a CSSStyleRule SelectorList.
Partly implements http://www.w3.org/TR/css3-selectors/.

TODO
    - .contains(selector)
    - .isSubselector(selector)
"""

from __future__ import annotations

__all__ = ['Selector']

import contextlib
import dataclasses
import xml.dom

import cssutils
from cssutils.helper import Deprecated
from cssutils.util import _SimpleNamespaces


class Constants:
    "expected constants"

    # used for equality checks and setting of a space combinator
    S = ' '

    simple_selector_sequence = (
        'type_selector universal HASH class ' 'attrib pseudo negation '
    )
    simple_selector_sequence2 = 'HASH class attrib pseudo negation '

    element_name = 'element_name'

    negation_arg = 'type_selector universal HASH class attrib pseudo'
    negationend = ')'

    attname = 'prefix attribute'
    attname2 = 'attribute'
    attcombinator = 'combinator ]'  # optional
    attvalue = 'value'  # optional
    attend = ']'

    expressionstart = 'PLUS - DIMENSION NUMBER STRING IDENT'
    expression = expressionstart + ' )'

    combinator = ' combinator'


@dataclasses.dataclass
class New(cssutils.util._BaseClass):
    """
    Derives from _BaseClass to provide self._log.
    """

    selector: Selector
    namespaces: dict[str, str]
    context: list[str] = dataclasses.field(default_factory=lambda: [''])
    "stack of: 'attrib', 'negation', 'pseudo'"
    element: str | None = None
    _PREFIX: str | None = None
    specificity: list[int] = dataclasses.field(default_factory=lambda: [0] * 4)
    "mutable, finally a tuple!"
    wellformed: bool = True

    def append(self, seq, val, typ=None, token=None):  # noqa: C901
        """
        appends to seq

        namespace_prefix, IDENT will be combined to a tuple
        (prefix, name) where prefix might be None, the empty string
        or a prefix.

        Saved are also:
            - specificity definition: style, id, class/att, type
            - element: the element this Selector is for
        """
        context = self.context[-1]
        if token:
            line, col = token[2], token[3]
        else:
            line, col = None, None

        if typ == '_PREFIX':
            # SPECIAL TYPE: save prefix for combination with next
            self._PREFIX = val[:-1]
            # handle next time
            return

        if self._PREFIX is not None:
            # as saved from before and reset to None
            prefix, self._PREFIX = self._PREFIX, None
        elif typ == 'universal' and '|' in val:
            # val == *|* or prefix|*
            prefix, val = val.split('|')
        else:
            prefix = None

        # namespace
        if (typ.endswith('-selector') or typ == 'universal') and not (
            'attribute-selector' == typ and not prefix
        ):
            # att **IS NOT** in default ns
            if prefix == '*':
                # *|name: in ANY_NS
                namespaceURI = cssutils._ANYNS
            elif prefix is None:
                # e or *: default namespace with prefix u''
                # or local-name()
                namespaceURI = self.namespaces.get('', None)
            elif prefix == '':
                # |name or |*: in no (or the empty) namespace
                namespaceURI = ''
            else:
                # explicit namespace prefix
                # does not raise KeyError, see _SimpleNamespaces
                namespaceURI = self.namespaces[prefix]

                if namespaceURI is None:
                    self.wellformed = False
                    self._log.error(
                        'Selector: No namespaceURI found ' 'for prefix %r' % prefix,
                        token=token,
                        error=xml.dom.NamespaceErr,
                    )
                    return

            # val is now (namespaceprefix, name) tuple
            val = (namespaceURI, val)

        # specificity
        if not context or context == 'negation':
            if 'id' == typ:
                self.specificity[1] += 1
            elif 'class' == typ or '[' == val:
                self.specificity[2] += 1
            elif typ in (
                'type-selector',
                'negation-type-selector',
                'pseudo-element',
            ):
                self.specificity[3] += 1
        if not context and typ in ('type-selector', 'universal'):
            # define element
            self.element = val

        seq.append(val, typ, line=line, col=col)

    def _COMMENT(self, expected, seq, token, tokenizer=None):
        "special implementation for comment token"
        self.append(seq, cssutils.css.CSSComment([token]), 'COMMENT', token=token)
        return expected

    def _S(self, expected, seq, token, tokenizer=None):
        # S
        context = self.context[-1]
        if context.startswith('pseudo-'):
            if seq and seq[-1].value not in '+-':
                # e.g. x:func(a + b)
                self.append(seq, Constants.S, 'S', token=token)
            return expected

        elif context != 'attrib' and 'combinator' in expected:
            self.append(seq, Constants.S, 'descendant', token=token)
            return Constants.simple_selector_sequence + Constants.combinator

        else:
            return expected

    def _universal(self, expected, seq, token, tokenizer=None):
        # *|* or prefix|*
        context = self.context[-1]
        val = self.selector._tokenvalue(token)
        if 'universal' in expected:
            self.append(seq, val, 'universal', token=token)

            if 'negation' == context:
                return Constants.negationend
            else:
                return Constants.simple_selector_sequence2 + Constants.combinator

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected universal.', token=token)
            return expected

    def _namespace_prefix(self, expected, seq, token, tokenizer=None):
        # prefix| => element_name
        # or prefix| => attribute_name if attrib
        context = self.context[-1]
        val = self.selector._tokenvalue(token)
        if 'attrib' == context and 'prefix' in expected:
            # [PREFIX|att]
            self.append(seq, val, '_PREFIX', token=token)
            return Constants.attname2
        elif 'type_selector' in expected:
            # PREFIX|*
            self.append(seq, val, '_PREFIX', token=token)
            return Constants.element_name
        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected namespace prefix.', token=token)
            return expected

    def _pseudo(self, expected, seq, token, tokenizer=None):
        # pseudo-class or pseudo-element :a ::a :a( ::a(
        """
        /* '::' starts a pseudo-element, ':' a pseudo-class */
        /* Exceptions: :first-line, :first-letter, :before and
        :after. */
        /* Note that pseudo-elements are restricted to one per selector
        and */
        /* occur only in the last simple_selector_sequence. */
        """
        context = self.context[-1]
        val, typ = (
            self.selector._tokenvalue(token, normalize=True),
            self.selector._type(token),
        )
        if 'pseudo' in expected:
            if val in (':first-line', ':first-letter', ':before', ':after'):
                # always pseudo-element ???
                typ = 'pseudo-element'
            self.append(seq, val, typ, token=token)

            if val.endswith('('):
                # function
                # "pseudo-" "class" or "element"
                self.context.append(typ)
                return Constants.expressionstart
            elif 'negation' == context:
                return Constants.negationend
            elif 'pseudo-element' == typ:
                # only one per element, check at ) also!
                return Constants.combinator
            else:
                return Constants.simple_selector_sequence2 + Constants.combinator

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected start of pseudo.', token=token)
            return expected

    def _expression(self, expected, seq, token, tokenizer=None):
        # [ [ PLUS | '-' | DIMENSION | NUMBER | STRING | IDENT ] S* ]+
        context = self.context[-1]
        val, typ = self.selector._tokenvalue(token), self.selector._type(token)
        if context.startswith('pseudo-'):
            self.append(seq, val, typ, token=token)
            return Constants.expression
        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected %s.' % typ, token=token)
            return expected

    def _attcombinator(self, expected, seq, token, tokenizer=None):
        # context: attrib
        # PREFIXMATCH | SUFFIXMATCH | SUBSTRINGMATCH | INCLUDES |
        # DASHMATCH
        context = self.context[-1]
        val, typ = self.selector._tokenvalue(token), self.selector._type(token)
        if 'attrib' == context and 'combinator' in expected:
            # combinator in attrib
            self.append(seq, val, typ.lower(), token=token)
            return Constants.attvalue
        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected %s.' % typ, token=token)
            return expected

    def _string(self, expected, seq, token, tokenizer=None):
        # identifier
        context = self.context[-1]
        typ, val = self.selector._type(token), self.selector._stringtokenvalue(token)

        # context: attrib
        if 'attrib' == context and 'value' in expected:
            # attrib: [...=VALUE]
            self.append(seq, val, typ, token=token)
            return Constants.attend

        # context: pseudo
        elif context.startswith('pseudo-'):
            # :func(...)
            self.append(seq, val, typ, token=token)
            return Constants.expression

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected STRING.', token=token)
            return expected

    def _ident(self, expected, seq, token, tokenizer=None):
        # identifier
        context = self.context[-1]
        val, typ = self.selector._tokenvalue(token), self.selector._type(token)

        # context: attrib
        if 'attrib' == context and 'attribute' in expected:
            # attrib: [...|ATT...]
            self.append(seq, val, 'attribute-selector', token=token)
            return Constants.attcombinator

        elif 'attrib' == context and 'value' in expected:
            # attrib: [...=VALUE]
            self.append(seq, val, 'attribute-value', token=token)
            return Constants.attend

        # context: negation
        elif 'negation' == context:
            # negation: (prefix|IDENT)
            self.append(seq, val, 'negation-type-selector', token=token)
            return Constants.negationend

        # context: pseudo
        elif context.startswith('pseudo-'):
            # :func(...)
            self.append(seq, val, typ, token=token)
            return Constants.expression

        elif 'type_selector' in expected or Constants.element_name == expected:
            # element name after ns or complete type_selector
            self.append(seq, val, 'type-selector', token=token)
            return Constants.simple_selector_sequence2 + Constants.combinator

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected IDENT.', token=token)
            return expected

    def _class(self, expected, seq, token, tokenizer=None):
        # .IDENT
        context = self.context[-1]
        val = self.selector._tokenvalue(token)
        if 'class' in expected:
            self.append(seq, val, 'class', token=token)

            if 'negation' == context:
                return Constants.negationend
            else:
                return Constants.simple_selector_sequence2 + Constants.combinator

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected class.', token=token)
            return expected

    def _hash(self, expected, seq, token, tokenizer=None):
        # #IDENT
        context = self.context[-1]
        val = self.selector._tokenvalue(token)
        if 'HASH' in expected:
            self.append(seq, val, 'id', token=token)

            if 'negation' == context:
                return Constants.negationend
            else:
                return Constants.simple_selector_sequence2 + Constants.combinator

        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected HASH.', token=token)
            return expected

    def _char(self, expected, seq, token, tokenizer=None):  # noqa: C901
        # + > ~ ) [ ] + -
        context = self.context[-1]
        val = self.selector._tokenvalue(token)

        # context: attrib
        if ']' == val and 'attrib' == context and ']' in expected:
            # end of attrib
            self.append(seq, val, 'attribute-end', token=token)
            context = self.context.pop()  # attrib is done
            context = self.context[-1]
            if 'negation' == context:
                return Constants.negationend
            else:
                return Constants.simple_selector_sequence2 + Constants.combinator

        if '=' == val and 'attrib' == context and 'combinator' in expected:
            # combinator in attrib
            self.append(seq, val, 'equals', token=token)
            return Constants.attvalue

        # context: negation
        if ')' == val and 'negation' == context and ')' in expected:
            # not(negation_arg)"
            self.append(seq, val, 'negation-end', token=token)
            self.context.pop()  # negation is done
            context = self.context[-1]
            return Constants.simple_selector_sequence + Constants.combinator

        # context: pseudo (at least one expression)
        if val in '+-' and context.startswith('pseudo-'):
            # :func(+ -)"
            _names = {'+': 'plus', '-': 'minus'}
            if val == '+' and seq and seq[-1].value == Constants.S:
                seq.replace(-1, val, _names[val])
            else:
                self.append(seq, val, _names[val], token=token)
            return Constants.expression

        if (
            ')' == val
            and context.startswith('pseudo-')
            and Constants.expression == expected
        ):
            # :func(expression)"
            self.append(seq, val, 'function-end', token=token)
            self.context.pop()  # pseudo is done
            if 'pseudo-element' == context:
                return Constants.combinator
            else:
                return Constants.simple_selector_sequence + Constants.combinator

        # context: ROOT
        if '[' == val and 'attrib' in expected:
            # start of [attrib]
            self.append(seq, val, 'attribute-start', token=token)
            self.context.append('attrib')
            return Constants.attname

        if val in '+>~' and 'combinator' in expected:
            # no other combinator except S may be following
            _names = {
                '>': 'child',
                '+': 'adjacent-sibling',
                '~': 'following-sibling',
            }
            if seq and seq[-1].value == Constants.S:
                seq.replace(-1, val, _names[val])
            else:
                self.append(seq, val, _names[val], token=token)
            return Constants.simple_selector_sequence

        if ',' == val:
            # not a selectorlist
            self.wellformed = False
            self._log.error(
                'Selector: Single selector only.',
                error=xml.dom.InvalidModificationErr,
                token=token,
            )
            return expected

        self.wellformed = False
        self._log.error('Selector: Unexpected CHAR.', token=token)
        return expected

    def _negation(self, expected, seq, token, tokenizer=None):
        # not(
        val = self.selector._tokenvalue(token, normalize=True)
        if 'negation' in expected:
            self.context.append('negation')
            self.append(seq, val, 'negation-start', token=token)
            return Constants.negation_arg
        else:
            self.wellformed = False
            self._log.error('Selector: Unexpected negation.', token=token)
            return expected

    def _atkeyword(self, expected, seq, token, tokenizer=None):
        "invalidates selector"
        self.wellformed = False
        self._log.error('Selector: Unexpected ATKEYWORD.', token=token)
        return expected

    @property
    def productions(self):
        return {
            'CHAR': self._char,
            'class': self._class,
            'HASH': self._hash,
            'STRING': self._string,
            'IDENT': self._ident,
            'namespace_prefix': self._namespace_prefix,
            'negation': self._negation,
            'pseudo-class': self._pseudo,
            'pseudo-element': self._pseudo,
            'universal': self._universal,
            # pseudo
            'NUMBER': self._expression,
            'DIMENSION': self._expression,
            # attribute
            'PREFIXMATCH': self._attcombinator,
            'SUFFIXMATCH': self._attcombinator,
            'SUBSTRINGMATCH': self._attcombinator,
            'DASHMATCH': self._attcombinator,
            'INCLUDES': self._attcombinator,
            'S': self._S,
            'COMMENT': self._COMMENT,
            'ATKEYWORD': self._atkeyword,
        }


class Selector(cssutils.util.Base2):
    """
    (cssutils) a single selector in a :class:`~cssutils.css.SelectorList`
    of a :class:`~cssutils.css.CSSStyleRule`.

    Format::

        # implemented in SelectorList
        selectors_group
          : selector [ COMMA S* selector ]*
          ;

        selector
          : simple_selector_sequence [ combinator simple_selector_sequence ]*
          ;

        combinator
          /* combinators can be surrounded by white space */
          : PLUS S* | GREATER S* | TILDE S* | S+
          ;

        simple_selector_sequence
          : [ type_selector | universal ]
            [ HASH | class | attrib | pseudo | negation ]*
          | [ HASH | class | attrib | pseudo | negation ]+
          ;

        type_selector
          : [ namespace_prefix ]? element_name
          ;

        namespace_prefix
          : [ IDENT | '*' ]? '|'
          ;

        element_name
          : IDENT
          ;

        universal
          : [ namespace_prefix ]? '*'
          ;

        class
          : '.' IDENT
          ;

        attrib
          : '[' S* [ namespace_prefix ]? IDENT S*
                [ [ PREFIXMATCH |
                    SUFFIXMATCH |
                    SUBSTRINGMATCH |
                    '=' |
                    INCLUDES |
                    DASHMATCH ] S* [ IDENT | STRING ] S*
                ]? ']'
          ;

        pseudo
          /* '::' starts a pseudo-element, ':' a pseudo-class */
          /* Exceptions: :first-line, :first-letter, :before and :after. */
          /* Note that pseudo-elements are restricted to one per selector and */
          /* occur only in the last simple_selector_sequence. */
          : ':' ':'? [ IDENT | functional_pseudo ]
          ;

        functional_pseudo
          : FUNCTION S* expression ')'
          ;

        expression
          /* In CSS3, the expressions are identifiers, strings, */
          /* or of the form "an+b" */
          : [ [ PLUS | '-' | DIMENSION | NUMBER | STRING | IDENT ] S* ]+
          ;

        negation
          : NOT S* negation_arg S* ')'
          ;

        negation_arg
          : type_selector | universal | HASH | class | attrib | pseudo
          ;

    """

    def __init__(self, selectorText=None, parent=None, readonly=False):
        """
        :Parameters:
            selectorText
                initial value of this selector
            parent
                a SelectorList
            readonly
                default to False
        """
        super().__init__()

        self.__namespaces = _SimpleNamespaces(log=self._log)
        self._element = None
        self._parent = parent
        self._specificity = (0, 0, 0, 0)

        if selectorText:
            self.selectorText = selectorText

        self._readonly = readonly

    def __repr__(self):
        if self.__getNamespaces():
            st = (self.selectorText, self._getUsedNamespaces())
        else:
            st = self.selectorText
        return f"cssutils.css.{self.__class__.__name__}(selectorText={st!r})"

    def __str__(self):
        return (
            "<cssutils.css.%s object selectorText=%r specificity=%r"
            " _namespaces=%r at 0x%x>"
            % (
                self.__class__.__name__,
                self.selectorText,
                self.specificity,
                self._getUsedNamespaces(),
                id(self),
            )
        )

    def _getUsedUris(self):
        "Return list of actually used URIs in this Selector."
        uris = set()
        for item in self.seq:
            type_, val = item.type, item.value
            if (
                type_.endswith('-selector')
                or type_ == 'universal'
                and isinstance(val, tuple)
                and val[0] not in (None, '*')
            ):
                uris.add(val[0])
        return uris

    def _getUsedNamespaces(self):
        "Return actually used namespaces only."
        useduris = self._getUsedUris()
        namespaces = _SimpleNamespaces(log=self._log)
        for p, uri in list(self._namespaces.items()):
            if uri in useduris:
                namespaces[p] = uri
        return namespaces

    def __getNamespaces(self):
        "Use own namespaces if not attached to a sheet, else the sheet's ones."
        try:
            return self._parent.parentRule.parentStyleSheet.namespaces
        except AttributeError:
            return self.__namespaces

    _namespaces = property(
        __getNamespaces,
        doc="If this Selector is attached to a "
        "CSSStyleSheet the namespaces of that sheet "
        "are mirrored here. While the Selector (or "
        "parent SelectorList or parentRule(s) of that "
        "are not attached a own dict of {prefix: "
        "namespaceURI} is used.",
    )

    @property
    def element(self):
        """Effective element target of this selector."""
        return self._element

    parent = property(
        lambda self: self._parent,
        doc="(DOM) The SelectorList that contains this Selector "
        "or None if this Selector is not attached to a "
        "SelectorList.",
    )

    def _getSelectorText(self):
        """Return serialized format."""
        return cssutils.ser.do_css_Selector(self)

    def _setSelectorText(self, selectorText):
        """
        :param selectorText:
            parsable string or a tuple of (selectorText, dict-of-namespaces).
            Given namespaces are ignored if this object is attached to a
            CSSStyleSheet!

        :exceptions:
            - :exc:`~xml.dom.NamespaceErr`:
              Raised if the specified selector uses an unknown namespace
              prefix.
            - :exc:`~xml.dom.SyntaxErr`:
              Raised if the specified CSS string value has a syntax error
              and is unparsable.
            - :exc:`~xml.dom.NoModificationAllowedErr`:
              Raised if this rule is readonly.
        """
        self._checkReadonly()

        # might be (selectorText, namespaces)
        selectorText, namespaces = self._splitNamespacesOff(selectorText)

        with contextlib.suppress(AttributeError):
            # uses parent stylesheets namespaces if available,
            # otherwise given ones
            namespaces = self.parent.parentRule.parentStyleSheet.namespaces

        tokenizer = self._tokenize2(selectorText)
        if not tokenizer:
            self._log.error('Selector: No selectorText given.')
            return

        tokenizer = self._prepare_tokens(tokenizer)

        new = New(selector=self, namespaces=namespaces)

        # expected: only|not or mediatype, mediatype, feature, and
        newseq = self._tempSeq()

        wellformed, expected = self._parse(
            expected=Constants.simple_selector_sequence,
            seq=newseq,
            tokenizer=tokenizer,
            productions=new.productions,
        )
        wellformed = wellformed and new.wellformed

        # post condition
        if len(new.context) > 1 or not newseq:
            wellformed = False
            self._log.error(
                'Selector: Invalid or incomplete selector: %s'
                % self._valuestr(selectorText)
            )

        if expected == 'element_name':
            wellformed = False
            self._log.error(
                'Selector: No element name found: %s' % self._valuestr(selectorText)
            )

        if expected == Constants.simple_selector_sequence and newseq:
            wellformed = False
            self._log.error(
                'Selector: Cannot end with combinator: %s'
                % self._valuestr(selectorText)
            )

        if (
            newseq
            and hasattr(newseq[-1].value, 'strip')
            and newseq[-1].value.strip() == ''
        ):
            del newseq[-1]

        # set
        if wellformed:
            self.__namespaces = namespaces
            self._element = new.element
            self._specificity = tuple(new.specificity)
            self._setSeq(newseq)
            # filter that only used ones are kept
            self.__namespaces = self._getUsedNamespaces()

    def _prepare_tokens(self, tokenizer):  # noqa: C901
        """
        "*" -> type "universal"
        "*"|IDENT + "|" -> combined to "namespace_prefix"
        "|" -> type "namespace_prefix"
        "." + IDENT -> combined to "class"
        ":" + IDENT, ":" + FUNCTION -> pseudo-class
        FUNCTION "not(" -> negation
        "::" + IDENT, "::" + FUNCTION -> pseudo-element
        """
        tokens = []
        for t in tokenizer:
            typ, val, lin, col = t
            if val == ':' and tokens and self._tokenvalue(tokens[-1]) == ':':
                # combine ":" and ":"
                tokens[-1] = (typ, '::', lin, col)

            elif typ == 'IDENT' and tokens and self._tokenvalue(tokens[-1]) == '.':
                # class: combine to .IDENT
                tokens[-1] = ('class', '.' + val, lin, col)
            elif (
                typ == 'IDENT'
                and tokens
                and self._tokenvalue(tokens[-1]).startswith(':')
                and not self._tokenvalue(tokens[-1]).endswith('(')
            ):
                # pseudo-X: combine to :IDENT or ::IDENT but not ":a(" + "b"
                if self._tokenvalue(tokens[-1]).startswith('::'):
                    t = 'pseudo-element'
                else:
                    t = 'pseudo-class'
                tokens[-1] = (t, self._tokenvalue(tokens[-1]) + val, lin, col)

            elif (
                typ == 'FUNCTION'
                and val == 'not('
                and tokens
                and ':' == self._tokenvalue(tokens[-1])
            ):
                tokens[-1] = ('negation', ':' + val, lin, tokens[-1][3])
            elif (
                typ == 'FUNCTION'
                and tokens
                and self._tokenvalue(tokens[-1]).startswith(':')
            ):
                # pseudo-X: combine to :FUNCTION( or ::FUNCTION(
                if self._tokenvalue(tokens[-1]).startswith('::'):
                    t = 'pseudo-element'
                else:
                    t = 'pseudo-class'
                tokens[-1] = (t, self._tokenvalue(tokens[-1]) + val, lin, col)

            elif (
                val == '*'
                and tokens
                and self._type(tokens[-1]) == 'namespace_prefix'
                and self._tokenvalue(tokens[-1]).endswith('|')
            ):
                # combine prefix|*
                tokens[-1] = (
                    'universal',
                    self._tokenvalue(tokens[-1]) + val,
                    lin,
                    col,
                )
            elif val == '*':
                # universal: "*"
                tokens.append(('universal', val, lin, col))

            elif (
                val == '|'
                and tokens
                and self._type(tokens[-1]) in (self._prods.IDENT, 'universal')
                and self._tokenvalue(tokens[-1]).find('|') == -1
            ):
                # namespace_prefix: "IDENT|" or "*|"
                tokens[-1] = (
                    'namespace_prefix',
                    self._tokenvalue(tokens[-1]) + '|',
                    lin,
                    col,
                )
            elif val == '|':
                # namespace_prefix: "|"
                tokens.append(('namespace_prefix', val, lin, col))

            else:
                tokens.append(t)

        return iter(tokens)

    selectorText = property(
        _getSelectorText,
        _setSelectorText,
        doc="(DOM) The parsable textual representation of " "the selector.",
    )

    specificity = property(
        lambda self: self._specificity,
        doc="""Specificity of this selector (READONLY).
                Tuple of (a, b, c, d) where:

                a
                    presence of style in document, always 0 if not used on a
                    document
                b
                    number of ID selectors
                c
                    number of .class selectors
                d
                    number of Element (type) selectors""",
    )

    wellformed = property(lambda self: bool(len(self.seq)))

    @Deprecated('Use property parent instead')
    def _getParentList(self):
        return self.parent

    parentList = property(_getParentList, doc="DEPRECATED, see property parent instead")
