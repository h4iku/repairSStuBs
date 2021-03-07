import unittest
from pathlib import Path

from utils.line_normalize import check_line


class TestLineNormalize(unittest.TestCase):

    def setUp(self):
        self.FIXS_ROOT = Path(__file__).parent / 'fixtures'

    def test_multicomment_before_line(self):
        result = 'void assertOnIndex(int index);'
        line_number = 24
        with open(self.FIXS_ROOT / 'AssertionTask.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_multicomment_before_multiline(self):
        result = 'public class LocalizedMessage implements Comparable {'
        line_number = 25
        with open(self.FIXS_ROOT / 'LocalizedMessage.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_multiline(self):
        result = 'String result = engine.execute( query ) .dumpToString();'
        line_number = 194
        with open(self.FIXS_ROOT / 'RolesTest.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_single_comment_before_multiline(self):
        result = ('if ("Notes".equals(subSectionName) || "Rule Description".equals(subSectionName)'
                  ' || "Metadata".equals(subSectionName)) {')
        line_number = 369
        with open(self.FIXS_ROOT / 'XdocsPagesTest.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_mixed_comment_between_multiline(self):
        result = 'public static final InputFastMatcher NONE = new InputFastMatcher() {'
        line_number = 36
        with open(self.FIXS_ROOT / 'InputIndentationCorrect.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_object_new(self):
        result = ('ProcessEngineConfigurator configurator = new SecureServiceTaskConfigurator() '
                  '.setWhiteListedShellCommands(new HashSet<String>(Arrays.asList("ls", "pwd")));')
        line_number = 31
        with open(self.FIXS_ROOT / 'SecureServiceTaskBaseTest.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_object_new_new(self):
        result = ('static final SensitiveTargetAccessConstraintDefinition WEB_CONNECTOR_CONSTRAINT ='
                  ' new SensitiveTargetAccessConstraintDefinition('
                  ' new SensitivityClassification(SUBSYSTEM_NAME, "web-connector", true, false, false));')
        line_number = 96
        with open(self.FIXS_ROOT / 'WebExtension.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_method_call(self):
        result = ('placeholderToken.set(TokenizerBenchmarkTestCase.MWTTokenCharacterOffsetEndAnnotation.class,'
                  ' containedToken.endPosition());')
        line_number = 155
        with open(self.FIXS_ROOT / 'TokenizerBenchmarkTestCase.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_enum_content(self):
        result = 'Never, IfReplyExpected, Always'
        line_number = 35
        with open(self.FIXS_ROOT / 'WaitForTaskToComplete.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_single_line(self):
        result = 'private static final Logger LOG = LoggerFactory.getLogger(DefaultManagementAgent.class);'
        line_number = 31
        with open(self.FIXS_ROOT / 'DefaultManagementMBeanAssembler.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_middle_line_multiline(self):
        result = ('return Collections.unmodifiableSet(new HashSet<>(Arrays.asList('
                  ' CoreAnnotations.TextAnnotation.class, CoreAnnotations.TokensAnnotation.class,'
                  ' CoreAnnotations.SentencesAnnotation.class, CoreAnnotations.CharacterOffsetBeginAnnotation.class,'
                  ' CoreAnnotations.CharacterOffsetEndAnnotation.class, CoreAnnotations.PartOfSpeechAnnotation.class,'
                  ' CoreAnnotations.LemmaAnnotation.class, CoreAnnotations.BeforeAnnotation.class,'
                  ' CoreAnnotations.AfterAnnotation.class, CoreAnnotations.TokenBeginAnnotation.class,'
                  ' CoreAnnotations.TokenEndAnnotation.class, CoreAnnotations.IndexAnnotation.class,'
                  ' CoreAnnotations.OriginalTextAnnotation.class, CoreAnnotations.SentenceIndexAnnotation.class,'
                  ' CoreAnnotations.IsNewlineAnnotation.class, CoreAnnotations.TokenIndexAnnotation.class )));')
        line_number = 366
        with open(self.FIXS_ROOT / 'NERCombinerAnnotator.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_if(self):
        result = ('if (cl.word().equals(gl.word()) && cl.beginPosition() == gl.beginPosition()'
                  ' && cl.endPosition() == gl.endPosition()) {')
        line_number = 196
        with open(self.FIXS_ROOT / 'TokenizerBenchmarkTestCase.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_assign1(self):
        result = ('boolean isSourceLocal = mLocalWorkerAddress.getHost().equals(request.getSourceHost())'
                  ' && mLocalWorkerAddress.getRpcPort() == request.getSourcePort();')
        line_number = 81
        with open(self.FIXS_ROOT / 'AsyncCacheRequestManager.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_last_line_multiline_assign2(self):
        result = ('final boolean nameMatches = ALL_WARNING_MATCHING_ID.equals(entry.getCheckName())'
                  ' || entry.getCheckName().equals(checkAlias);')
        line_number = 166
        with open(self.FIXS_ROOT / 'SuppressWarningsHolder.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_middle_line_multiline_new(self):
        result = ('languageSpecificPrimitives = new HashSet<String>('
                  ' Arrays.asList( "bool", "qint32", "qint64") );')
        line_number = 97
        with open(self.FIXS_ROOT / 'Qt5CPPGenerator.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_closing_bracket_before_line(self):
        result = ('if (StringUtils.isEmpty(formKey)) {')
        line_number = 336
        with open(self.FIXS_ROOT / 'DeploymentServiceImpl.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_closing_bracket_on_end_line(self):
        result = ('return finalFormKey;')
        line_number = 340
        with open(self.FIXS_ROOT / 'DeploymentServiceImpl.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_case_colon_before_line(self):
        result = ('free(path, false);')
        line_number = 3049
        with open(self.FIXS_ROOT / 'FileSystemMaster.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    def test_case_colon_on_line(self):
        result = ('case FREE:')
        line_number = 3048
        with open(self.FIXS_ROOT / 'FileSystemMaster.java') as f:
            lines = f.read().splitlines()
        normed_lines = check_line(lines, line_number - 1)
        self.assertEqual(normed_lines[line_number - 1], result)

    # These two tests break the regex and keep the code in a loop.
    # In the first one, the given line number is actually in the middle of a multiline comment!
    # The second one is in the middle of a huge Enum.

    # def test_middle_multiline_comment1(self):
    #     result = 'Paint paint = new Paint();'
    #     line_number = 71
    #     with open(self.FIXS_ROOT / 'PorterDuff.java') as f:
    #         lines = f.read().splitlines()
    #     normed_lines = check_line(lines, line_number - 1)
    #     self.assertEqual(normed_lines[line_number - 1], result)

    # def test_middle_multiline_enum(self):
    #     result = ''
    #     line_number = 175
    #     with open(self.FIXS_ROOT / 'Cipher.java') as f:
    #         lines = f.read().splitlines()
    #     normed_lines = check_line(lines, line_number - 1)
    #     self.assertEqual(normed_lines[line_number - 1], result)
