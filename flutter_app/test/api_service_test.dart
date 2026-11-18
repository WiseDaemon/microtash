import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:microstash/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('ApiService Tests with Mock HTTP Client', () {
    test('fetchIdeas returns list of Idea models on HTTP 200', () async {
      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/ideas'));
        if (request.url.queryParameters.containsKey('topic')) {
          expect(request.url.queryParameters['topic'], equals('Strategy'));
        }

        final responsePayload = [
          {
            'id': 'idea_1',
            'title': 'First-Principles Thinking',
            'one_liner': 'Reason from fundamental axioms.',
            'summary': 'Deconstruct problems to their base components.',
            'author': 'Elon Musk',
            'source': 'SpaceX',
            'copyright_notice': 'Commentary',
            'topic': 'Strategy',
            'tags': ['Strategy', 'Logic'],
            'leitner_box': 1,
            'next_review_date': '2026-11-20',
          },
          {
            'id': 'idea_2',
            'title': 'Inversion',
            'one_liner': 'Invert, always invert.',
            'summary': 'Think backwards from failure.',
            'author': 'Charlie Munger',
            'source': 'Almanack',
            'copyright_notice': 'Commentary',
            'topic': 'Strategy',
            'tags': ['Strategy'],
            'leitner_box': 2,
            'next_review_date': '2026-11-21',
          }
        ];

        return http.Response(jsonEncode(responsePayload), 200, headers: {'content-type': 'application/json'});
      });

      final ideas = await ApiService.fetchIdeas(topic: 'Strategy');

      expect(ideas, hasLength(2));
      expect(ideas[0].id, equals('idea_1'));
      expect(ideas[0].title, equals('First-Principles Thinking'));
      expect(ideas[1].id, equals('idea_2'));
      expect(ideas[1].title, equals('Inversion'));
    });

    test('fetchIdeas handles network error gracefully with offline fallback', () async {
      ApiService.client = MockClient((request) async {
        return http.Response('Internal Server Error', 500);
      });

      final ideas = await ApiService.fetchIdeas();
      // Returns offline cache (empty when uninitialized) without throwing an uncaught exception
      expect(ideas, isA<List>());
    });

    test('fetchBooks sends search query and parses book models', () async {
      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/books'));
        expect(request.url.queryParameters['search'], equals('Thinking'));

        final responsePayload = [
          {
            'id': 'book_1',
            'title': 'Thinking, Fast and Slow',
            'normalized_title': 'thinking fast and slow',
            'author': 'Daniel Kahneman',
            'publisher': 'FSG',
            'copyright_notice': 'Summary and commentary.',
            'topic': 'Psychology',
            'ideas_count': 5,
            'scanned_by_user': 'community',
            'scanned_at': '2026-11-18T00:00:00Z',
            'scan_status': 'completed',
            'ideas': [],
          }
        ];

        return http.Response(jsonEncode(responsePayload), 200, headers: {'content-type': 'application/json'});
      });

      final books = await ApiService.fetchBooks(search: 'Thinking');

      expect(books, hasLength(1));
      expect(books[0].title, equals('Thinking, Fast and Slow'));
      expect(books[0].author, equals('Daniel Kahneman'));
    });

    test('fetchBookDetail returns Book with nested ideas on 200 or null on 404', () async {
      ApiService.client = MockClient((request) async {
        if (request.url.path == '/api/books/antifragile') {
          final payload = {
            'id': 'book_antifragile',
            'title': 'Antifragile',
            'normalized_title': 'antifragile',
            'author': 'Nassim Taleb',
            'publisher': 'Random House',
            'copyright_notice': 'Commentary',
            'topic': 'Risk',
            'ideas_count': 1,
            'scanned_by_user': 'taleb_fan',
            'scanned_at': '2026-11-18T00:00:00Z',
            'scan_status': 'completed',
            'ideas': [
              {
                'id': 'idea_anti_1',
                'title': 'Barbell Strategy',
                'one_liner': 'Combine extreme safety with asymmetric upside.',
                'summary': 'Avoid the middle ground of moderate risk.',
                'author': 'Nassim Taleb',
                'source': 'Antifragile',
                'copyright_notice': 'Summary',
                'topic': 'Risk',
                'tags': ['Strategy'],
              }
            ],
          };
          return http.Response(jsonEncode(payload), 200);
        } else {
          return http.Response('Not Found', 404);
        }
      });

      final book = await ApiService.fetchBookDetail('antifragile');
      expect(book, isNotNull);
      expect(book!.title, equals('Antifragile'));
      expect(book.ideas, hasLength(1));
      expect(book.ideas[0].title, equals('Barbell Strategy'));

      final missing = await ApiService.fetchBookDetail('non-existent');
      expect(missing, isNull);
    });

    test('fetchDueLeitner returns due ideas for cognitive workout', () async {
      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/ideas/leitner/due'));

        final payload = [
          {
            'id': 'idea_due_1',
            'title': 'Second-Order Thinking',
            'one_liner': 'And then what?',
            'summary': 'Consider long-term secondary consequences.',
            'author': 'Howard Marks',
            'source': 'The Most Important Thing',
            'copyright_notice': 'Summary',
            'topic': 'Strategy',
            'tags': ['Decisions'],
            'leitner_box': 1,
            'next_review_date': '2026-11-18',
          }
        ];

        return http.Response(jsonEncode(payload), 200);
      });

      final dueCards = await ApiService.fetchDueLeitner();
      expect(dueCards, hasLength(1));
      expect(dueCards[0].title, equals('Second-Order Thinking'));
    });

    test('submitLeitnerReview posts grade rating for idea', () async {
      bool reviewed = false;

      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/ideas/idea_101/leitner-review'));
        expect(request.method, equals('POST'));

        final body = jsonDecode(request.body);
        expect(body['grade'], equals(5));

        reviewed = true;
        return http.Response(jsonEncode({'status': 'ok'}), 200);
      });

      final result = await ApiService.submitLeitnerReview('idea_101', 5);
      expect(result, isTrue);
      expect(reviewed, isTrue);
    });

    test('fetchStressTest retrieves Socratic scenario and options', () async {
      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/ai/stress-test/idea_second_order'));

        final payload = {
          'stress_test': {
            'scenario': 'Your quarterly revenue drops 15% after a product price hike.',
            'question': 'How do you apply Second-Order Thinking?',
            'options': [
              {'id': 'A', 'text': 'Slash prices immediately to recover volume.', 'is_correct': false, 'feedback': 'First-order trap.'},
              {'id': 'B', 'text': 'Analyze churn composition and long-term customer LTV.', 'is_correct': true, 'feedback': 'Correct! Second-order analysis.'}
            ],
            'first_principles_takeaway': 'Evaluate downstream effects over multiple time horizons.'
          }
        };

        return http.Response(jsonEncode(payload), 200);
      });

      final dilemma = await ApiService.fetchStressTest('idea_second_order');
      expect(dilemma, isNotNull);
      expect(dilemma!['scenario'], contains('quarterly revenue'));
      expect(dilemma['options'], hasLength(2));
      expect(dilemma['first_principles_takeaway'], contains('downstream effects'));
    });

    test('login authenticates user and extracts access_token', () async {
      ApiService.client = MockClient((request) async {
        expect(request.url.path, equals('/api/auth/login'));
        final body = jsonDecode(request.body);
        expect(body['username_or_email'], equals('learner@microstash.app'));
        expect(body['password'], equals('ValidPass123'));

        return http.Response(
          jsonEncode({
            'status': 'ok',
            'access_token': 'jwt_mock_token_abc_123',
            'user': {'username': 'learner', 'email': 'learner@microstash.app'},
          }),
          200,
        );
      });

      final loginRes = await ApiService.login('learner@microstash.app', 'ValidPass123');
      expect(loginRes, isNotNull);
      expect(loginRes!['access_token'], equals('jwt_mock_token_abc_123'));
      expect(loginRes['user']['username'], equals('learner'));
    });

    test('toggleLike and toggleSave execute POST requests successfully', () async {
      int likeCount = 0;
      int saveCount = 0;

      ApiService.client = MockClient((request) async {
        if (request.url.path == '/api/ideas/idea_xyz/like') {
          likeCount++;
          return http.Response(jsonEncode({'is_liked': true, 'likes': 5}), 200);
        }
        if (request.url.path == '/api/ideas/idea_xyz/save') {
          saveCount++;
          return http.Response(jsonEncode({'is_saved': true, 'saved_count': 2}), 200);
        }
        return http.Response('Not Found', 404);
      });

      final likeOk = await ApiService.toggleLike('idea_xyz');
      final saveOk = await ApiService.toggleSave('idea_xyz');

      expect(likeOk, isTrue);
      expect(saveOk, isTrue);
      expect(likeCount, equals(1));
      expect(saveCount, equals(1));
    });
  });
}
