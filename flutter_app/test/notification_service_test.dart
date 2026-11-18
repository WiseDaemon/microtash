import 'package:flutter_test/flutter_test.dart';
import 'package:microstash/services/notification_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    NotificationService.lastAlert = null;
  });

  group('NotificationService Tests', () {
    test('triggerInstantRecallAlert stores alert and broadcasts on stream', () async {
      Map<String, dynamic>? streamedAlert;
      final sub = NotificationService.alertStreamController.stream.listen((alert) {
        streamedAlert = alert;
      });

      await NotificationService.triggerInstantRecallAlert(
        title: '🧠 Cognitive Gym: 3 Mental Models Due',
        body: '3 minutes of active recall today!',
      );

      expect(NotificationService.lastAlert, isNotNull);
      expect(NotificationService.lastAlert!['title'], contains('3 Mental Models Due'));
      expect(NotificationService.lastAlert!['channel'], equals('microstash_recall_channel'));

      final prefs = await SharedPreferences.getInstance();
      expect(prefs.getString('microstash_last_alert_title'), contains('3 Mental Models Due'));

      // Wait a tick for stream event
      await Future.delayed(const Duration(milliseconds: 10));
      expect(streamedAlert, isNotNull);
      expect(streamedAlert!['title'], contains('3 Mental Models Due'));

      await sub.cancel();
    });

    test('checkDueCardsAndNotify triggers alert and prevents duplicate same-day alerts', () async {
      // First check with 4 due cards: should trigger
      await NotificationService.checkDueCardsAndNotify(4);
      expect(NotificationService.lastAlert, isNotNull);
      expect(NotificationService.lastAlert!['title'], contains('4 Mental Models Due'));

      // Clear lastAlert to verify second call on same day
      NotificationService.lastAlert = null;
      await NotificationService.checkDueCardsAndNotify(4);
      // Should not trigger again today
      expect(NotificationService.lastAlert, isNull);
    });

    test('evaluateScheduledReminder triggers at target hour or past, even with hourly jitter', () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('microstash_reminder_hour', 9);
      await prefs.setInt('microstash_reminder_minute', 0);
      await prefs.setBool('microstash_reminder_enabled', true);

      // 1. Before reminder time (08:30): should NOT trigger
      final beforeTime = DateTime(2026, 11, 18, 8, 30);
      final triggeredBefore = await NotificationService.evaluateScheduledReminder(beforeTime);
      expect(triggeredBefore, isFalse);
      expect(NotificationService.lastAlert, isNull);

      // 2. Exactly at or past target hour (e.g. 09:35, where previous bug (35-0).abs() < 30 failed!):
      // With our fix, 09:35 correctly triggers!
      final jitteredTime = DateTime(2026, 11, 18, 9, 35);
      final triggeredAtJitter = await NotificationService.evaluateScheduledReminder(jitteredTime);
      expect(triggeredAtJitter, isTrue);
      expect(NotificationService.lastAlert, isNotNull);
      expect(NotificationService.lastAlert!['title'], contains('Daily Mental Model Workout'));

      // 3. Second evaluation later on the same day (10:00): should NOT trigger again
      NotificationService.lastAlert = null;
      final laterTime = DateTime(2026, 11, 18, 10, 0);
      final triggeredLater = await NotificationService.evaluateScheduledReminder(laterTime);
      expect(triggeredLater, isFalse);
      expect(NotificationService.lastAlert, isNull);
    });
  });
}
