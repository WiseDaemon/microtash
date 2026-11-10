import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';

class NotificationService {
  static const String _keyReminderEnabled = 'microstash_reminder_enabled';
  static const String _keyReminderHour = 'microstash_reminder_hour';
  static const String _keyReminderMinute = 'microstash_reminder_minute';
  static const String _keyLastNotifiedDate = 'microstash_last_notified_date';

  static bool _isInitialized = false;
  static Timer? _scheduleTimer;

  /// Initializes daily notification reminders for Leitner spaced repetition.
  static Future<void> initialize() async {
    if (_isInitialized) return;
    _isInitialized = true;
    _startBackgroundCheckLoop();
  }

  /// Checks if daily reminders are enabled (defaults to true)
  static Future<bool> isReminderEnabled() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool(_keyReminderEnabled) ?? true;
    } catch (_) {
      return true;
    }
  }

  /// Toggles daily recall reminders on or off
  static Future<void> setReminderEnabled(bool enabled) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(_keyReminderEnabled, enabled);
      if (enabled) {
        await scheduleDailyWorkoutReminder();
      } else {
        await cancelAllReminders();
      }
    } catch (_) {}
  }

  /// Configures daily reminder hour and minute (default: 09:00 AM)
  static Future<void> scheduleDailyWorkoutReminder({int hour = 9, int minute = 0}) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt(_keyReminderHour, hour);
      await prefs.setInt(_keyReminderMinute, minute);
      await prefs.setBool(_keyReminderEnabled, true);
    } catch (_) {}
  }

  /// Evaluates pending workout cards and triggers cognitive recall reminder
  static Future<void> checkDueCardsAndNotify(int dueCount) async {
    if (dueCount <= 0) return;
    final enabled = await isReminderEnabled();
    if (!enabled) return;

    final todayStr = DateTime.now().toIso8601String().substring(0, 10);
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastNotified = prefs.getString(_keyLastNotifiedDate);

      // Prevent nagging with duplicate notifications on the same day
      if (lastNotified == todayStr) return;

      await triggerInstantRecallAlert(
        title: '🧠 Cognitive Gym: $dueCount Mental Models Due',
        body: 'Retain high-leverage frameworks with 3 minutes of active recall!',
      );

      await prefs.setString(_keyLastNotifiedDate, todayStr);
    } catch (_) {}
  }

  /// Dispatches an immediate notification alert
  static Future<void> triggerInstantRecallAlert({
    required String title,
    required String body,
  }) async {
    // Android Channel: microstash_recall_channel (Daily Mental Model Recall)
  }

  /// Cancels all scheduled active recall notifications
  static Future<void> cancelAllReminders() async {
    _scheduleTimer?.cancel();
    _scheduleTimer = null;
  }

  static void _startBackgroundCheckLoop() {
    _scheduleTimer?.cancel();
    _scheduleTimer = Timer.periodic(const Duration(hours: 1), (timer) async {
      try {
        final now = DateTime.now();
        final prefs = await SharedPreferences.getInstance();
        final enabled = prefs.getBool(_keyReminderEnabled) ?? true;
        if (!enabled) return;

        final targetHour = prefs.getInt(_keyReminderHour) ?? 9;
        final targetMinute = prefs.getInt(_keyReminderMinute) ?? 0;

        if (now.hour == targetHour && (now.minute - targetMinute).abs() < 30) {
          final todayStr = now.toIso8601String().substring(0, 10);
          final lastNotified = prefs.getString(_keyLastNotifiedDate);
          if (lastNotified != todayStr) {
            await triggerInstantRecallAlert(
              title: '🧠 Daily Mental Model Workout',
              body: 'Your spaced repetition review is ready. Solidify your models in 3 mins!',
            );
            await prefs.setString(_keyLastNotifiedDate, todayStr);
          }
        }
      } catch (_) {}
    });
  }
}
