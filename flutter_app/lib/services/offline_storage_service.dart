import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/idea.dart';
import '../models/book.dart';

class OfflineStorageService {
  static const String _keyIdeas = 'microstash_cached_ideas';
  static const String _keyBooks = 'microstash_cached_books';
  static const String _keyDueLeitner = 'microstash_cached_due_leitner';
  static const String _keyPendingReviews = 'microstash_pending_reviews';
  static const String _keyAuthToken = 'microstash_auth_token';

  /// Saves the active user session JWT token
  static Future<void> saveAuthToken(String token) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_keyAuthToken, token);
    } catch (_) {}
  }

  /// Retrieves the active user session JWT token
  static Future<String?> getAuthToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_keyAuthToken);
    } catch (_) {}
    return null;
  }

  /// Clears stored authentication session token
  static Future<void> clearAuthToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_keyAuthToken);
    } catch (_) {}
  }

  /// Saves ideas list permanently to disk
  static Future<void> saveIdeas(List<Idea> ideas) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = ideas.map((e) => e.toJson()).toList();
      await prefs.setString(_keyIdeas, jsonEncode(list));
    } catch (_) {}
  }

  /// Loads cached ideas from disk (works 100% offline)
  static Future<List<Idea>> loadIdeas() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString(_keyIdeas);
      if (str != null && str.isNotEmpty) {
        final List list = jsonDecode(str);
        return list.map((e) => Idea.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Saves books list permanently to disk
  static Future<void> saveBooks(List<Book> books) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = books.map((e) => e.toJson()).toList();
      await prefs.setString(_keyBooks, jsonEncode(list));
    } catch (_) {}
  }

  /// Loads cached books from disk
  static Future<List<Book>> loadBooks() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString(_keyBooks);
      if (str != null && str.isNotEmpty) {
        final List list = jsonDecode(str);
        return list.map((e) => Book.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Saves active recall workout cards
  static Future<void> saveDueLeitner(List<Idea> due) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final list = due.map((e) => e.toJson()).toList();
      await prefs.setString(_keyDueLeitner, jsonEncode(list));
    } catch (_) {}
  }

  /// Loads workout cards
  static Future<List<Idea>> loadDueLeitner() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final str = prefs.getString(_keyDueLeitner);
      if (str != null && str.isNotEmpty) {
        final List list = jsonDecode(str);
        return list.map((e) => Idea.fromJson(e)).toList();
      }
    } catch (_) {}
    return [];
  }

  /// Queues a review rating when offline so user progress is never lost
  static Future<void> queueOfflineReview(String ideaId, int grade) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final queueStr = prefs.getString(_keyPendingReviews) ?? '[]';
      final List queue = jsonDecode(queueStr);
      queue.add({
        'idea_id': ideaId,
        'grade': grade,
        'timestamp': DateTime.now().toIso8601String(),
      });
      await prefs.setString(_keyPendingReviews, jsonEncode(queue));
    } catch (_) {}
  }

  /// Returns pending reviews that occurred while offline
  static Future<List<Map<String, dynamic>>> getPendingReviews() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final queueStr = prefs.getString(_keyPendingReviews) ?? '[]';
      final List queue = jsonDecode(queueStr);
      return queue.map((e) => Map<String, dynamic>.from(e)).toList();
    } catch (_) {}
    return [];
  }

  /// Clears review queue after successful server sync
  static Future<void> clearPendingReviews() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_keyPendingReviews);
    } catch (_) {}
  }
}
