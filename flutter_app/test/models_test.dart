import 'package:flutter_test/flutter_test.dart';
import 'package:microstash/models/idea.dart';
import 'package:microstash/models/book.dart';

void main() {
  group('Idea Model Tests', () {
    test('Idea.fromJson deserializes all canonical fields correctly', () {
      final json = {
        'id': 'idea_first_principles',
        'title': 'First-Principles Thinking',
        'one_liner': 'Boil a problem down to the most fundamental truths and reason up.',
        'summary': 'Rather than reasoning by analogy, deconstruct assumptions into axioms.',
        'detailed_explanation': 'Aristotle defined first principles as the first basis from which a thing is known.',
        'example': 'SpaceX calculating the raw material cost of rockets (2% of retail price).',
        'visual_diagram': 'graph TD\n  A[Challenge Problem] --> B[Deconstruct to Axioms]',
        'quote': 'I think it is important to reason from first principles rather than by analogy. — Elon Musk',
        'action_item': 'List the 3 fundamental physical or economic constraints of your current blocker.',
        'author': 'Aristotle & Elon Musk',
        'source': 'Physics & SpaceX Biographies',
        'source_slug': 'first-principles',
        'publisher': 'Ancient Philosophy & Modern Tech',
        'copyright_notice': 'Transformative educational commentary based on Physics.',
        'topic': 'Mental Models',
        'tags': ['Strategy', 'Reasoning', 'Innovation'],
        'read_time_mins': 3,
        'color_theme': 'indigo',
        'likes': 42,
        'saved_count': 18,
        'is_liked': 1,
        'is_saved': 1,
        'leitner_box': 3,
        'next_review_date': '2026-11-25',
        'boundary': 'Ineffective for chaotic survival situations requiring immediate heuristic reflex.',
      };

      final idea = Idea.fromJson(json);

      expect(idea.id, equals('idea_first_principles'));
      expect(idea.title, equals('First-Principles Thinking'));
      expect(idea.oneLiner, contains('fundamental truths'));
      expect(idea.summary, contains('reasoning by analogy'));
      expect(idea.detailedExplanation, contains('Aristotle'));
      expect(idea.example, contains('SpaceX'));
      expect(idea.visualDiagram, contains('graph TD'));
      expect(idea.quote, contains('Elon Musk'));
      expect(idea.actionItem, contains('fundamental physical'));
      expect(idea.author, equals('Aristotle & Elon Musk'));
      expect(idea.source, equals('Physics & SpaceX Biographies'));
      expect(idea.sourceSlug, equals('first-principles'));
      expect(idea.publisher, equals('Ancient Philosophy & Modern Tech'));
      expect(idea.copyrightNotice, contains('Transformative educational commentary'));
      expect(idea.topic, equals('Mental Models'));
      expect(idea.tags, equals(['Strategy', 'Reasoning', 'Innovation']));
      expect(idea.readTimeMins, equals(3));
      expect(idea.colorTheme, equals('indigo'));
      expect(idea.likes, equals(42));
      expect(idea.savedCount, equals(18));
      expect(idea.isLiked, isTrue);
      expect(idea.isSaved, isTrue);
      expect(idea.leitnerBox, equals(3));
      expect(idea.nextReviewDate, equals('2026-11-25'));
    });

    test('Idea.fromJson handles default values when optional fields are null or omitted', () {
      final minimalJson = {
        'id': 'idea_minimal',
        'title': 'Minimal Model',
        'one_liner': 'Short premise',
        'summary': 'Short summary',
      };

      final idea = Idea.fromJson(minimalJson);

      expect(idea.id, equals('idea_minimal'));
      expect(idea.title, equals('Minimal Model'));
      expect(idea.author, equals('Thinker'));
      expect(idea.source, equals('Book'));
      expect(idea.publisher, equals('Original Publication'));
      expect(idea.topic, equals('Mental Models'));
      expect(idea.tags, isEmpty);
      expect(idea.readTimeMins, equals(1));
      expect(idea.colorTheme, equals('indigo'));
      expect(idea.likes, equals(0));
      expect(idea.savedCount, equals(0));
      expect(idea.isLiked, isFalse);
      expect(idea.isSaved, isFalse);
      expect(idea.leitnerBox, equals(1));
      expect(idea.nextReviewDate, isNull);
      expect(idea.detailedExplanation, isNull);
      expect(idea.visualDiagram, isNull);
    });

    test('Idea.fromJson converts boolean fields from integer or boolean formats', () {
      final jsonInts = {
        'id': 'idea_bool_1',
        'title': 'Bool Test 1',
        'one_liner': 'Test',
        'summary': 'Test',
        'is_liked': 1,
        'is_saved': 0,
      };
      final idea1 = Idea.fromJson(jsonInts);
      expect(idea1.isLiked, isTrue);
      expect(idea1.isSaved, isFalse);

      final jsonBools = {
        'id': 'idea_bool_2',
        'title': 'Bool Test 2',
        'one_liner': 'Test',
        'summary': 'Test',
        'is_liked': false,
        'is_saved': true,
      };
      final idea2 = Idea.fromJson(jsonBools);
      expect(idea2.isLiked, isFalse);
      expect(idea2.isSaved, isTrue);
    });

    test('Idea handles boundary strings and Leitner spaced repetition progressions', () {
      final boundaryJson = {
        'id': 'idea_boundary',
        'title': 'Chesterton Fence',
        'one_liner': 'Do not remove a fence until you know why it was put up.',
        'summary': 'Reforms must be preceded by understanding the original purpose.',
        'leitner_box': 5,
        'next_review_date': '2026-12-31',
        'boundary': 'Does not apply to immediate life-threatening security vulnerabilities or hazardous hazards.',
      };

      final idea = Idea.fromJson(boundaryJson);
      expect(idea.leitnerBox, equals(5));
      expect(idea.nextReviewDate, equals('2026-12-31'));

      final serialized = idea.toJson();
      expect(serialized['id'], equals('idea_boundary'));
      expect(serialized['leitner_box'], equals(5));
      expect(serialized['next_review_date'], equals('2026-12-31'));
    });

    test('Idea.toJson preserves all data during roundtrip serialization', () {
      final original = Idea(
        id: 'idea_roundtrip',
        title: 'Inversion Principle',
        oneLiner: 'Invert, always invert.',
        summary: 'Avoid stupidity rather than seeking brilliance.',
        detailedExplanation: 'Carl Jacobi advised inverting mathematical problems.',
        author: 'Charlie Munger & Carl Jacobi',
        source: 'Poor Charlie\'s Almanack',
        sourceSlug: 'inversion',
        publisher: 'WSA',
        copyrightNotice: 'Fair use commentary.',
        topic: 'Strategy',
        tags: ['Decision Making', 'Munger'],
        readTimeMins: 2,
        colorTheme: 'amber',
        likes: 12,
        savedCount: 5,
        isLiked: true,
        isSaved: false,
        leitnerBox: 2,
        nextReviewDate: '2026-11-20',
      );

      final json = original.toJson();
      final reconstructed = Idea.fromJson(json);

      expect(reconstructed.id, equals(original.id));
      expect(reconstructed.title, equals(original.title));
      expect(reconstructed.oneLiner, equals(original.oneLiner));
      expect(reconstructed.summary, equals(original.summary));
      expect(reconstructed.author, equals(original.author));
      expect(reconstructed.source, equals(original.source));
      expect(reconstructed.leitnerBox, equals(original.leitnerBox));
      expect(reconstructed.nextReviewDate, equals(original.nextReviewDate));
      expect(reconstructed.isLiked, equals(original.isLiked));
      expect(reconstructed.isSaved, equals(original.isSaved));
    });
  });

  group('Book Model Tests', () {
    test('Book.fromJson deserializes valid book payload with nested ideas', () {
      final bookJson = {
        'id': 'book_thinking_fast_slow',
        'title': 'Thinking, Fast and Slow',
        'normalized_title': 'thinking fast and slow',
        'author': 'Daniel Kahneman',
        'publisher': 'Farrar, Straus and Giroux',
        'copyright_notice': 'Educational commentary and summary of Thinking, Fast and Slow by Daniel Kahneman.',
        'description': 'A masterclass in behavioral psychology and dual-process cognitive architecture.',
        'cover_url': 'https://example.com/cover.jpg',
        'topic': 'Psychology',
        'ideas_count': 2,
        'scanned_by_user': 'alyssa',
        'scanned_at': '2026-11-18T10:00:00Z',
        'scan_status': 'completed',
        'ideas': [
          {
            'id': 'idea_system_1_2',
            'title': 'System 1 and System 2 Thinking',
            'one_liner': 'Fast, instinctive cognition vs slow, deliberate calculation.',
            'summary': 'Two cognitive systems govern human decision making.',
            'author': 'Daniel Kahneman',
            'source': 'Thinking, Fast and Slow',
            'copyright_notice': 'Fair use summary.',
            'topic': 'Psychology',
            'tags': ['Biases', 'Heuristics'],
          },
          {
            'id': 'idea_loss_aversion',
            'title': 'Loss Aversion',
            'one_liner': 'Losses hurt roughly 2 to 2.5 times more than equivalent gains please.',
            'summary': 'The psychological pain of losing is asymmetric.',
            'author': 'Daniel Kahneman',
            'source': 'Thinking, Fast and Slow',
            'copyright_notice': 'Fair use summary.',
            'topic': 'Psychology',
            'tags': ['Economics', 'Biases'],
          }
        ],
        'stash_id': 'stash_kahneman_library',
      };

      final book = Book.fromJson(bookJson);

      expect(book.id, equals('book_thinking_fast_slow'));
      expect(book.title, equals('Thinking, Fast and Slow'));
      expect(book.normalizedTitle, equals('thinking fast and slow'));
      expect(book.author, equals('Daniel Kahneman'));
      expect(book.publisher, equals('Farrar, Straus and Giroux'));
      expect(book.topic, equals('Psychology'));
      expect(book.ideasCount, equals(2));
      expect(book.ideas.length, equals(2));
      expect(book.ideas[0].title, equals('System 1 and System 2 Thinking'));
      expect(book.ideas[1].title, equals('Loss Aversion'));
      expect(book.scannedByUser, equals('alyssa'));
      expect(book.scanStatus, equals('completed'));
      expect(book.stashId, equals('stash_kahneman_library'));
    });

    test('Book.fromJson applies sensible defaults for missing fields', () {
      final minimalJson = {
        'id': 'book_minimal',
        'title': 'Minimal Book',
        'author': 'Jane Author',
      };

      final book = Book.fromJson(minimalJson);

      expect(book.id, equals('book_minimal'));
      expect(book.title, equals('Minimal Book'));
      expect(book.author, equals('Jane Author'));
      expect(book.publisher, equals('Original Publication'));
      expect(book.topic, equals('Mental Models'));
      expect(book.ideasCount, equals(0));
      expect(book.ideas, isEmpty);
      expect(book.copyrightNotice, contains('Jane Author'));
      expect(book.scannedByUser, equals('community'));
      expect(book.scanStatus, equals('completed'));
    });

    test('Book.toJson roundtrip serialization maintains structure', () {
      final book = Book(
        id: 'book_antifragile',
        title: 'Antifragile',
        normalizedTitle: 'antifragile',
        author: 'Nassim Nicholas Taleb',
        publisher: 'Random House',
        copyrightNotice: 'Attribution to Nassim Nicholas Taleb.',
        description: 'Things that gain from disorder.',
        topic: 'Risk',
        ideasCount: 1,
        scannedByUser: 'user_taleb',
        scannedAt: '2026-11-18T12:00:00Z',
        scanStatus: 'completed',
        ideas: [
          Idea(
            id: 'idea_antifragility',
            title: 'Antifragility',
            oneLiner: 'Some things benefit from shocks; they thrive when exposed to volatility.',
            summary: 'Beyond resilience and robustness.',
            author: 'Nassim Nicholas Taleb',
            source: 'Antifragile',
            copyrightNotice: 'Fair use.',
            topic: 'Risk',
            tags: ['Volatility', 'Asymmetry'],
          ),
        ],
      );

      final json = book.toJson();
      final restored = Book.fromJson(json);

      expect(restored.id, equals(book.id));
      expect(restored.title, equals(book.title));
      expect(restored.author, equals(book.author));
      expect(restored.ideas.length, equals(1));
      expect(restored.ideas[0].title, equals('Antifragility'));
    });
  });
}
