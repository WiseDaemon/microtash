import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:microstash/main.dart';
import 'package:microstash/screens/discover_screen.dart';
import 'package:microstash/screens/feed_screen.dart';
import 'package:microstash/screens/workout_screen.dart';
import 'package:microstash/services/api_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});

    // Configure deterministic mock responses for API service
    ApiService.client = MockClient((request) async {
      if (request.url.path == '/api/ideas') {
        return http.Response(
          jsonEncode([
            {
              'id': 'idea_test_1',
              'title': 'First-Principles Thinking',
              'one_liner': 'Reason from fundamental axioms.',
              'summary': 'Deconstruct problems to fundamental truths.',
              'author': 'Aristotle',
              'source': 'Physics',
              'copyright_notice': 'Commentary',
              'topic': 'Mental Models',
              'tags': ['Logic'],
            }
          ]),
          200,
          headers: {'content-type': 'application/json'},
        );
      } else if (request.url.path == '/api/books') {
        return http.Response(
          jsonEncode([
            {
              'id': 'book_test_1',
              'title': 'Thinking, Fast and Slow',
              'normalized_title': 'thinking fast and slow',
              'author': 'Daniel Kahneman',
              'publisher': 'FSG',
              'copyright_notice': 'Commentary',
              'topic': 'Psychology',
              'ideas_count': 1,
              'scanned_by_user': 'community',
              'scanned_at': '2026-11-18T00:00:00Z',
              'scan_status': 'completed',
              'ideas': [],
            }
          ]),
          200,
          headers: {'content-type': 'application/json'},
        );
      } else if (request.url.path == '/api/ideas/leitner/due') {
        // Return empty list so workout shows the completion screen
        return http.Response(jsonEncode([]), 200, headers: {'content-type': 'application/json'});
      }
      return http.Response('Not Found', 404);
    });
  });

  group('MicrostashApp Widget & Navigation Tests', () {
    testWidgets('App initializes cleanly and renders 3 navigation destinations', (WidgetTester tester) async {
      await tester.pumpWidget(const MicrostashApp());
      await tester.pumpAndSettle();

      // Verify MaterialApp title and theme
      expect(find.byType(MaterialApp), findsOneWidget);
      expect(find.byType(MainNavigationShell), findsOneWidget);

      // Verify the 3 bottom navigation destinations
      expect(find.text('Gym Feed'), findsOneWidget);
      expect(find.text('Discover Books'), findsOneWidget);
      expect(find.text('Daily Workout'), findsOneWidget);

      // Verify FeedScreen is active by default
      expect(find.byType(FeedScreen), findsOneWidget);
      expect(find.text('MICROSTASH'), findsOneWidget);
    });

    testWidgets('Switching tabs to Discover Books renders book search screen', (WidgetTester tester) async {
      await tester.pumpWidget(const MicrostashApp());
      await tester.pumpAndSettle();

      // Tap on 'Discover Books' tab
      await tester.tap(find.text('Discover Books'));
      await tester.pumpAndSettle();

      // Verify DiscoverScreen is active and search bar is present
      expect(find.byType(DiscoverScreen), findsOneWidget);
      expect(find.text('Global Book Library'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('Switching tabs to Daily Workout and tapping Return to Feed switches back to Feed tab without crashing', (WidgetTester tester) async {
      await tester.pumpWidget(const MicrostashApp());
      await tester.pumpAndSettle();

      // Tap on 'Daily Workout' tab (tab index 2)
      await tester.tap(find.text('Daily Workout'));
      await tester.pumpAndSettle();

      // Verify WorkoutScreen renders
      expect(find.byType(WorkoutScreen), findsOneWidget);
      expect(find.text('Daily Cognitive Workout Complete!'), findsOneWidget);

      // Find the 'Return to Feed' button
      final returnButton = find.widgetWithText(ElevatedButton, 'Return to Feed');
      expect(returnButton, findsOneWidget);

      // Tap 'Return to Feed'
      // Prior bug: called Navigator.pop(context) inside IndexedStack, which crashed the root route.
      // Fixed: calls onReturnToFeed callback, cleanly switching _currentIndex to 0.
      await tester.tap(returnButton);
      await tester.pumpAndSettle();

      // Verify we returned to Gym Feed
      expect(find.text('MICROSTASH'), findsOneWidget);
      expect(find.byType(MainNavigationShell), findsOneWidget);
    });
  });
}
