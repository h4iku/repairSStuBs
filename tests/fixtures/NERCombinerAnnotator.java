package edu.stanford.nlp.pipeline;

import edu.stanford.nlp.util.logging.Redwood;

import edu.stanford.nlp.ie.NERClassifierCombiner;
import edu.stanford.nlp.ie.regexp.NumberSequenceClassifier;
import edu.stanford.nlp.ling.CoreAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.tokensregex.types.Tags;
import edu.stanford.nlp.time.TimeAnnotations;
import edu.stanford.nlp.time.TimeExpression;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.util.PropertiesUtils;
import edu.stanford.nlp.util.RuntimeInterruptedException;

import java.io.IOException;
import java.util.*;
import java.util.regex.*;
import java.text.SimpleDateFormat;

/**
 * This class will add NER information to an Annotation using a combination of NER models.
 * It assumes that the Annotation already contains the tokenized words in sentences
 * under {@code CoreAnnotations.SentencesAnnotation.class} as
 * {@code List<? extends CoreLabel>}} or a
 * {@code List<List<? extends CoreLabel>>} under {@code Annotation.WORDS_KEY}
 * and adds NER information to each CoreLabel,
 * in the {@code CoreLabel.NER_KEY} field.  It uses
 * the NERClassifierCombiner class in the ie package.
 *
 * @author Jenny Finkel
 * @author Mihai Surdeanu (modified it to work with the new NERClassifierCombiner)
 */
public class NERCombinerAnnotator extends SentenceAnnotator  {

  /** A logger for this class */
  private static final Redwood.RedwoodChannels log = Redwood.channels(NERCombinerAnnotator.class);

  private final NERClassifierCombiner ner;

  private final boolean VERBOSE;
  private boolean usePresentDateForDocDate = false;
  private String providedDocDate = "";

  private final long maxTime;
  private final int nThreads;
  private final int maxSentenceLength;
  private LanguageInfo.HumanLanguage language = LanguageInfo.HumanLanguage.ENGLISH;

  /** Spanish NER enhancements **/
  private static final Map<String, String> spanishToEnglishTag = new HashMap<>();

  static {
    spanishToEnglishTag.put("PERS", "PERSON");
    spanishToEnglishTag.put("ORG", "ORGANIZATION");
    spanishToEnglishTag.put("LUG", "LOCATION");
    spanishToEnglishTag.put("OTROS", "MISC");

  }

  private static final String spanishNumberRegexRules =
      "edu/stanford/nlp/models/kbp/spanish/kbp_regexner_number_sp.tag";

  private TokensRegexNERAnnotator spanishNumberAnnotator;

  /** fine grained ner **/
  private boolean applyFineGrained = true;
  private TokensRegexNERAnnotator fineGrainedNERAnnotator;

  /** entity mentions **/
  private boolean buildEntityMentions = true;
  private EntityMentionsAnnotator entityMentionsAnnotator;

  public NERCombinerAnnotator(Properties properties) throws IOException {

    List<String> models = new ArrayList<>();
    String modelNames = properties.getProperty("ner.model");
    if (modelNames == null) {
      modelNames = DefaultPaths.DEFAULT_NER_THREECLASS_MODEL + ',' + DefaultPaths.DEFAULT_NER_MUC_MODEL + ',' + DefaultPaths.DEFAULT_NER_CONLL_MODEL;
    }
    if ( ! modelNames.isEmpty()) {
      models.addAll(Arrays.asList(modelNames.split(",")));
    }
    if (models.isEmpty()) {
      // Allow for no real NER model - can just use numeric classifiers or SUTime.
      // Have to unset ner.model, so unlikely that people got here by accident.
      log.info("WARNING: no NER models specified");
    }

    boolean applyNumericClassifiers =
        PropertiesUtils.getBool(properties,
            NERClassifierCombiner.APPLY_NUMERIC_CLASSIFIERS_PROPERTY,
            NERClassifierCombiner.APPLY_NUMERIC_CLASSIFIERS_DEFAULT);

    boolean applyRegexner =
        PropertiesUtils.getBool(properties,
            NERClassifierCombiner.APPLY_GAZETTE_PROPERTY,
            NERClassifierCombiner.APPLY_GAZETTE_DEFAULT);

    boolean useSUTime =
        PropertiesUtils.getBool(properties,
            NumberSequenceClassifier.USE_SUTIME_PROPERTY,
            NumberSequenceClassifier.USE_SUTIME_DEFAULT);

    // option for setting doc date to be the present during each annotation
    usePresentDateForDocDate =
        PropertiesUtils.getBool(properties, "ner." + "usePresentDateForDocDate", false);

    // option for setting doc date from a provided string
    providedDocDate = PropertiesUtils.getString(properties, "ner." + "providedDocDate", "");
    Pattern p = Pattern.compile("[0-9]{4}\\-[0-9]{2}\\-[0-9]{2}");
    Matcher m = p.matcher(providedDocDate);
    if (!m.matches())
      providedDocDate = "";

    NERClassifierCombiner.Language nerLanguage = NERClassifierCombiner.Language.fromString(PropertiesUtils.getString(properties,
        NERClassifierCombiner.NER_LANGUAGE_PROPERTY, null), NERClassifierCombiner.NER_LANGUAGE_DEFAULT);

    boolean verbose = PropertiesUtils.getBool(properties, "ner." + "verbose", false);

    String[] loadPaths = models.toArray(new String[models.size()]);

    Properties combinerProperties = PropertiesUtils.extractSelectedProperties(properties,
        NERClassifierCombiner.DEFAULT_PASS_DOWN_PROPERTIES);
    if (useSUTime) {
      // Make sure SUTime parameters are included
      Properties sutimeProps = PropertiesUtils.extractPrefixedProperties(properties, NumberSequenceClassifier.SUTIME_PROPERTY  + '.', true);
      PropertiesUtils.overWriteProperties(combinerProperties, sutimeProps);
    }
    NERClassifierCombiner nerCombiner = new NERClassifierCombiner(applyNumericClassifiers, nerLanguage,
        useSUTime, applyRegexner, combinerProperties, loadPaths);

    this.nThreads = PropertiesUtils.getInt(properties, "ner.nthreads", PropertiesUtils.getInt(properties, "nthreads", 1));
    this.maxTime = PropertiesUtils.getLong(properties, "ner.maxtime", 0);
    this.maxSentenceLength = PropertiesUtils.getInt(properties, "ner.maxlen", Integer.MAX_VALUE);
    this.language =
        LanguageInfo.getLanguageFromString(PropertiesUtils.getString(properties, "ner.language", "en"));

    // in case of Spanish, use the Spanish number regexner annotator
    if (language.equals(LanguageInfo.HumanLanguage.SPANISH)) {
      Properties spanishNumberRegexNerProperties = new Properties();
      spanishNumberRegexNerProperties.put("spanish.number.regexner.mapping", spanishNumberRegexRules);
      spanishNumberRegexNerProperties.put("spanish.number.regexner.validpospattern",
          "^(NUM).*");
      spanishNumberRegexNerProperties.put("spanish.number.regexner.ignorecase", "true");
      spanishNumberAnnotator = new TokensRegexNERAnnotator("spanish.number.regexner",
          spanishNumberRegexNerProperties);
    }

    // set up fine grained ner
    setUpFineGrainedNER(properties);

    // set up entity mentions
    setUpEntityMentionBuilding(properties);

    VERBOSE = verbose;
    this.ner = nerCombiner;
  }


  public NERCombinerAnnotator() throws IOException, ClassNotFoundException {
    this(true);
  }

  public NERCombinerAnnotator(boolean verbose) throws IOException, ClassNotFoundException {
    this(new NERClassifierCombiner(new Properties()), verbose);
  }

  public NERCombinerAnnotator(boolean verbose, String... classifiers)
    throws IOException, ClassNotFoundException
  {
    this(new NERClassifierCombiner(classifiers), verbose);
  }

  public NERCombinerAnnotator(NERClassifierCombiner ner, boolean verbose) {
    this(ner, verbose, 1, 0, Integer.MAX_VALUE);
  }

  public NERCombinerAnnotator(NERClassifierCombiner ner, boolean verbose, int nThreads, long maxTime) {
    this(ner, verbose, nThreads, maxTime, Integer.MAX_VALUE);
  }

  public NERCombinerAnnotator(NERClassifierCombiner ner, boolean verbose, int nThreads, long maxTime, int maxSentenceLength) {
    this(ner, verbose, nThreads, maxTime, maxSentenceLength, true, true);
  }

  public NERCombinerAnnotator(NERClassifierCombiner ner, boolean verbose, int nThreads, long maxTime,
                              int maxSentenceLength, boolean fineGrained, boolean entityMentions) {
    VERBOSE = verbose;
    this.ner = ner;
    this.maxTime = maxTime;
    this.nThreads = nThreads;
    this.maxSentenceLength = maxSentenceLength;
    Properties nerProperties = new Properties();
    nerProperties.setProperty("ner.applyFineGrained", Boolean.toString(fineGrained));
    nerProperties.setProperty("ner.buildEntityMentions", Boolean.toString(entityMentions));
    setUpFineGrainedNER(nerProperties);
    setUpEntityMentionBuilding(nerProperties);
  }

  public void setUpFineGrainedNER(Properties properties) {
    // set up fine grained ner
    this.applyFineGrained = PropertiesUtils.getBool(properties, "ner.applyFineGrained", true);
    if (this.applyFineGrained) {
      String fineGrainedPrefix = "ner.fine.regexner";
      Properties fineGrainedProps =
          PropertiesUtils.extractPrefixedProperties(properties, fineGrainedPrefix+".", true);
      fineGrainedNERAnnotator = new TokensRegexNERAnnotator(fineGrainedPrefix, fineGrainedProps);
    }
  }

  public void setUpEntityMentionBuilding(Properties properties) {
    this.buildEntityMentions = PropertiesUtils.getBool(properties, "ner.buildEntityMentions", true);
    if (this.buildEntityMentions) {
      String entityMentionsPrefix = "ner.entitymentions";
      Properties entityMentionsProps =
          PropertiesUtils.extractPrefixedProperties(properties, entityMentionsPrefix+".", true);
      // pass language info to the entity mention annotator
      entityMentionsProps.setProperty("ner.entitymentions.language", language.name());
      entityMentionsAnnotator = new EntityMentionsAnnotator(entityMentionsPrefix, entityMentionsProps);
    }
  }


  @Override
  protected int nThreads() {
    return nThreads;
  }

  @Override
  protected long maxTime() {
    return maxTime;
  }

  @Override
  public void annotate(Annotation annotation) {
    if (VERBOSE) {
      log.info("Adding NER Combiner annotation ... ");
    }

    // if ner.usePresentDateForDocDate is set, use the present date as the doc date
    if (usePresentDateForDocDate) {
      String currentDate =
          new SimpleDateFormat("yyyy-MM-dd").format(Calendar.getInstance().getTime());
      annotation.set(CoreAnnotations.DocDateAnnotation.class, currentDate);
    }
    // use provided doc date if applicable
    if (!providedDocDate.equals("")) {
      annotation.set(CoreAnnotations.DocDateAnnotation.class, providedDocDate);
    }

    super.annotate(annotation);
    this.ner.finalizeAnnotation(annotation);

    if (VERBOSE) {
      log.info("done.");
    }
    // if Spanish, run the regexner with Spanish number rules
    if (LanguageInfo.HumanLanguage.SPANISH.equals(language))
      spanishNumberAnnotator.annotate(annotation);
    // if fine grained ner is requested, run that
    if (this.applyFineGrained) {
      fineGrainedNERAnnotator.annotate(annotation);
      // set the FineGrainedNamedEntityTagAnnotation.class
      for (CoreLabel token : annotation.get(CoreAnnotations.TokensAnnotation.class)) {
        String fineGrainedTag = token.get(CoreAnnotations.NamedEntityTagAnnotation.class);
        token.set(CoreAnnotations.FineGrainedNamedEntityTagAnnotation.class, fineGrainedTag);
      }
    }
    // if entity mentions should be built, run that
    if (this.buildEntityMentions)
      entityMentionsAnnotator.annotate(annotation);
  }

  /** convert Spanish tag content of older models **/
  public String spanishToEnglishTag(String spanishTag) {
    if (spanishToEnglishTag.containsKey(spanishTag))
      return spanishToEnglishTag.get(spanishTag);
    else
      return spanishTag;
  }

  @Override
  public void doOneSentence(Annotation annotation, CoreMap sentence) {
    List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
    List<CoreLabel> output; // only used if try assignment works.
    if (tokens.size() <= this.maxSentenceLength) {
      try {
        output = this.ner.classifySentenceWithGlobalInformation(tokens, annotation, sentence);
      } catch (RuntimeInterruptedException e) {
        // If we get interrupted, set the NER labels to the background
        // symbol if they are not already set, then exit.
        output = null;
      }
    } else {
      output = null;
    }
    if (output == null) {
      doOneFailedSentence(annotation, sentence);
    } else {
      for (int i = 0, sz = tokens.size(); i < sz; ++i) {
        // add the named entity tag to each token
        String neTag = output.get(i).get(CoreAnnotations.NamedEntityTagAnnotation.class);
        String normNeTag = output.get(i).get(CoreAnnotations.NormalizedNamedEntityTagAnnotation.class);
        if (language.equals(LanguageInfo.HumanLanguage.SPANISH)) {
          neTag = spanishToEnglishTag(neTag);
          normNeTag = spanishToEnglishTag(normNeTag);
        }
        tokens.get(i).setNER(neTag);
        tokens.get(i).set(CoreAnnotations.CoarseNamedEntityTagAnnotation.class, neTag);
        if (normNeTag != null) tokens.get(i).set(CoreAnnotations.NormalizedNamedEntityTagAnnotation.class, normNeTag);
        NumberSequenceClassifier.transferAnnotations(output.get(i), tokens.get(i));
      }

      if (VERBOSE) {
        boolean first = true;
        StringBuilder sb = new StringBuilder("NERCombinerAnnotator output: [");
        for (CoreLabel w : tokens) {
          if (first) {
            first = false;
          } else {
            sb.append(", ");
          }
          sb.append(w.toShorterString("Text", "NamedEntityTag", "NormalizedNamedEntityTag"));
        }
        sb.append(']');
        log.info(sb);
      }
    }
  }

  /** {@inheritDoc} */
  @Override
  public void doOneFailedSentence(Annotation annotation, CoreMap sentence) {
    List<CoreLabel> tokens = sentence.get(CoreAnnotations.TokensAnnotation.class);
    for (CoreLabel token : tokens) {
      // add the background named entity tag to each token if it doesn't have an NER tag.
      if (token.ner() == null) {
        token.setNER(this.ner.backgroundSymbol());
      }
    }
  }


  @Override
  public Set<Class<? extends CoreAnnotation>> requires() {
    // TODO: we could check the models to see which ones use lemmas
    // and which ones use pos tags
    if (ner.usesSUTime() || ner.appliesNumericClassifiers()) {
      return Collections.unmodifiableSet(new HashSet<>(Arrays.asList(
          CoreAnnotations.TextAnnotation.class,
          CoreAnnotations.TokensAnnotation.class,
          CoreAnnotations.SentencesAnnotation.class,
          CoreAnnotations.CharacterOffsetBeginAnnotation.class,
          CoreAnnotations.CharacterOffsetEndAnnotation.class,
          CoreAnnotations.PartOfSpeechAnnotation.class,
          CoreAnnotations.LemmaAnnotation.class,
          CoreAnnotations.BeforeAnnotation.class,
          CoreAnnotations.AfterAnnotation.class,
          CoreAnnotations.TokenBeginAnnotation.class,
          CoreAnnotations.TokenEndAnnotation.class,
          CoreAnnotations.IndexAnnotation.class,
          CoreAnnotations.OriginalTextAnnotation.class,
          CoreAnnotations.SentenceIndexAnnotation.class,
          CoreAnnotations.IsNewlineAnnotation.class,
          CoreAnnotations.TokenIndexAnnotation.class
      )));
    } else {
      return Collections.unmodifiableSet(new HashSet<>(Arrays.asList(
          CoreAnnotations.TextAnnotation.class,
          CoreAnnotations.TokensAnnotation.class,
          CoreAnnotations.SentencesAnnotation.class,
          CoreAnnotations.CharacterOffsetBeginAnnotation.class,
          CoreAnnotations.CharacterOffsetEndAnnotation.class,
          CoreAnnotations.BeforeAnnotation.class,
          CoreAnnotations.AfterAnnotation.class,
          CoreAnnotations.TokenBeginAnnotation.class,
          CoreAnnotations.TokenEndAnnotation.class,
          CoreAnnotations.IndexAnnotation.class,
          CoreAnnotations.OriginalTextAnnotation.class,
          CoreAnnotations.SentenceIndexAnnotation.class,
          CoreAnnotations.IsNewlineAnnotation.class,
          CoreAnnotations.TokenIndexAnnotation.class
      )));
    }
  }

  @SuppressWarnings("unchecked")
  @Override
  public Set<Class<? extends CoreAnnotation>> requirementsSatisfied() {
    HashSet<Class<? extends CoreAnnotation>> nerRequirementsSatisfied =
        new HashSet<>(Arrays.asList(
        CoreAnnotations.NamedEntityTagAnnotation.class,
        CoreAnnotations.NormalizedNamedEntityTagAnnotation.class,
        CoreAnnotations.ValueAnnotation.class,
        TimeExpression.Annotation.class,
        TimeExpression.TimeIndexAnnotation.class,
        CoreAnnotations.DistSimAnnotation.class,
        CoreAnnotations.NumericCompositeTypeAnnotation.class,
        TimeAnnotations.TimexAnnotation.class,
        CoreAnnotations.NumericValueAnnotation.class,
        TimeExpression.ChildrenAnnotation.class,
        CoreAnnotations.NumericTypeAnnotation.class,
        CoreAnnotations.ShapeAnnotation.class,
        Tags.TagsAnnotation.class,
        CoreAnnotations.NumerizedTokensAnnotation.class,
        CoreAnnotations.AnswerAnnotation.class,
        CoreAnnotations.NumericCompositeValueAnnotation.class,
        CoreAnnotations.CoarseNamedEntityTagAnnotation.class,
        CoreAnnotations.FineGrainedNamedEntityTagAnnotation.class
        ));
    if (this.buildEntityMentions) {
      nerRequirementsSatisfied.add(CoreAnnotations.MentionsAnnotation.class);
      nerRequirementsSatisfied.add(CoreAnnotations.EntityTypeAnnotation.class);
      nerRequirementsSatisfied.add(CoreAnnotations.EntityMentionIndexAnnotation.class);
    }
    return nerRequirementsSatisfied;
  }

}
