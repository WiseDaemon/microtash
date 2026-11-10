import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/idea.dart';
import '../models/book.dart';
import 'offline_storage_service.dart';

class ApiService {
  // 10.0.2.2 maps to localhost from the Android Emulator; configure your live server domain for release
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<List<Idea>> fetchIdeas({String? topic, String? query}) async {
    try {
      final uri = Uri.parse('$baseUrl/api/ideas').replace(queryParameters: {
        if (topic != null && topic != 'All' && topic != 'all') 'topic': topic,
        if (query != null && query.isNotEmpty) 'search': query,
      });

      final res = await http.get(uri).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final ideas = data.map((e) => Idea.fromJson(e)).toList();
        if (ideas.isNotEmpty) {
          // Persist to local disk for 100% offline access
          await OfflineStorageService.saveIdeas(ideas);
        }
        // Attempt background sync of any reviews made while offline
        syncPendingReviews();
        return ideas;
      }
    } catch (_) {}

    // Fallback to disk storage when offline
    final offlineIdeas = await OfflineStorageService.loadIdeas();
    if (topic != null && topic != 'All' && topic != 'all') {
      return offlineIdeas.where((i) => i.topic.toLowerCase() == topic.toLowerCase()).toList();
    }
    return offlineIdeas;
  }

  static Future<List<Book>> fetchBooks({String? topic, String? search}) async {
    try {
      final uri = Uri.parse('$baseUrl/api/books').replace(queryParameters: {
        if (topic != null && topic.isNotEmpty) 'topic': topic,
        if (search != null && search.isNotEmpty) 'search': search,
      });

      final res = await http.get(uri).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final books = data.map((e) => Book.fromJson(e)).toList();
        if (books.isNotEmpty) {
          await OfflineStorageService.saveBooks(books);
        }
        return books;
      }
    } catch (_) {}

    return await OfflineStorageService.loadBooks();
  }

  static Future<Book?> fetchBookDetail(String slug) async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/books/$slug')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return Book.fromJson(jsonDecode(res.body));
      }
    } catch (_) {}
    return null;
  }

  static Future<Map<String, dynamic>?> lookupBook(String query) async {
    try {
      final uri = Uri.parse('$baseUrl/api/books/lookup').replace(queryParameters: {'query': query});
      final res = await http.get(uri).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (_) {}
    return null;
  }

  static Future<List<Idea>> fetchDueLeitner() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/ideas/leitner/due')).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final due = data.map((e) => Idea.fromJson(e)).toList();
        await OfflineStorageService.saveDueLeitner(due);
        return due;
      }
    } catch (_) {}

    return await OfflineStorageService.loadDueLeitner();
  }

  static Future<Map<String, dynamic>?> fetchStressTest(String ideaId) async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/api/ai/stress-test/$ideaId')).timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        return jsonDecode(res.body)['stress_test'];
      }
    } catch (_) {}
    return null;
  }

  static Future<bool> submitLeitnerReview(String ideaId, int grade) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/ideas/$ideaId/leitner-review'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'grade': grade}),
      ).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        return true;
      }
    } catch (_) {}

    // Queue offline review to persist user progress on device
    await OfflineStorageService.queueOfflineReview(ideaId, grade);
    return true;
  }

  /// Syncs offline ratings when connection is re-established
  static Future<void> syncPendingReviews() async {
    final pending = await OfflineStorageService.getPendingReviews();
    if (pending.isEmpty) return;

    bool allSynced = true;
    for (final review in pending) {
      try {
        final res = await http.post(
          Uri.parse('$baseUrl/api/ideas/${review['idea_id']}/leitner-review'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'grade': review['grade']}),
        ).timeout(const Duration(seconds: 3));
        if (res.statusCode != 200) allSynced = false;
      } catch (_) {
        allSynced = false;
        break;
      }
    }

    if (allSynced) {
      await OfflineStorageService.clearPendingReviews();
    }
  }

  /// 1-Click Deconstruction for content shared via Android Share Intent
  static Future<Map<String, dynamic>?> deconstructSharedContent(String text) async {
    try {
      final res = await http.post(
        Uri.parse('$baseUrl/api/ai/auto-fetch-and-generate'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'query': text,
          'topic': 'Mental Models',
          'provider': 'gemini',
        }),
      ).timeout(const Duration(seconds: 15));

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (_) {}
    return null;
  }

  static Future<bool> toggleLike(String ideaId) async {
    try {
      final res = await http.post(Uri.parse('$baseUrl/api/ideas/$ideaId/like'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  static Future<bool> toggleSave(String ideaId) async {
    try {
      final res = await http.post(Uri.parse('$baseUrl/api/ideas/$ideaId/save'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
