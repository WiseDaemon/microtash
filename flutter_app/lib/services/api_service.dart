import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/idea.dart';
import '../models/book.dart';
import 'offline_storage_service.dart';

class ApiService {
  // 10.0.2.2 maps to localhost from the Android Emulator; configure your live server domain for release
  static const String baseUrl = 'http://10.0.2.2:8000';

  /// HTTP client instance used for requests. May be overridden in unit tests with a MockClient.
  static http.Client client = http.Client();

  /// Helper to get request headers with optional Bearer JWT token
  static Future<Map<String, String>> _getHeaders([Map<String, String>? extra]) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      ...?extra,
    };
    final token = await OfflineStorageService.getAuthToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  // --- AUTHENTICATION & SESSION MANAGEMENT ---

  static Future<Map<String, dynamic>?> login(String usernameOrEmail, String password) async {
    try {
      final res = await client.post(
        Uri.parse('$baseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username_or_email': usernameOrEmail,
          'password': password,
        }),
      ).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (data['access_token'] != null) {
          await OfflineStorageService.saveAuthToken(data['access_token']);
        }
        return data;
      }
    } catch (e) {
      debugPrint('ApiService.login error: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> register({
    required String email,
    required String username,
    required String password,
    String? fullName,
  }) async {
    try {
      final res = await client.post(
        Uri.parse('$baseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'username': username,
          'password': password,
          'full_name': fullName,
        }),
      ).timeout(const Duration(seconds: 5));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (data['access_token'] != null) {
          await OfflineStorageService.saveAuthToken(data['access_token']);
        }
        return data;
      }
    } catch (e) {
      debugPrint('ApiService.register error: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> getCurrentUser() async {
    try {
      final headers = await _getHeaders();
      final res = await client.get(
        Uri.parse('$baseUrl/api/auth/me'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (e) {
      debugPrint('ApiService.getCurrentUser error: $e');
    }
    return null;
  }

  static Future<void> logout() async {
    try {
      final headers = await _getHeaders();
      await client.post(
        Uri.parse('$baseUrl/api/auth/logout'),
        headers: headers,
      ).timeout(const Duration(seconds: 3));
    } catch (e) {
      debugPrint('ApiService.logout error: $e');
    }
    await OfflineStorageService.clearAuthToken();
  }

  // --- IDEAS & BOOKS ---

  static Future<List<Idea>> fetchIdeas({String? topic, String? query}) async {
    try {
      final uri = Uri.parse('$baseUrl/api/ideas').replace(queryParameters: {
        if (topic != null && topic != 'All' && topic != 'all') 'topic': topic,
        if (query != null && query.isNotEmpty) 'search': query,
      });

      final headers = await _getHeaders();
      final res = await client.get(uri, headers: headers).timeout(const Duration(seconds: 4));
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
    } catch (e) {
      debugPrint('ApiService.fetchIdeas network error (falling back to offline): $e');
    }

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

      final headers = await _getHeaders();
      final res = await client.get(uri, headers: headers).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final books = data.map((e) => Book.fromJson(e)).toList();
        if (books.isNotEmpty) {
          await OfflineStorageService.saveBooks(books);
        }
        return books;
      }
    } catch (e) {
      debugPrint('ApiService.fetchBooks network error (falling back to offline): $e');
    }

    return await OfflineStorageService.loadBooks();
  }

  static Future<Book?> fetchBookDetail(String slug) async {
    try {
      final headers = await _getHeaders();
      final res = await client.get(
        Uri.parse('$baseUrl/api/books/$slug'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return Book.fromJson(jsonDecode(res.body));
      }
    } catch (e) {
      debugPrint('ApiService.fetchBookDetail error: $e');
    }
    return null;
  }

  static Future<Map<String, dynamic>?> lookupBook(String query) async {
    try {
      final uri = Uri.parse('$baseUrl/api/books/lookup').replace(queryParameters: {'query': query});
      final headers = await _getHeaders();
      final res = await client.get(uri, headers: headers).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (e) {
      debugPrint('ApiService.lookupBook error: $e');
    }
    return null;
  }

  static Future<List<Idea>> fetchDueLeitner() async {
    try {
      final headers = await _getHeaders();
      final res = await client.get(
        Uri.parse('$baseUrl/api/ideas/leitner/due'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List data = jsonDecode(res.body);
        final due = data.map((e) => Idea.fromJson(e)).toList();
        await OfflineStorageService.saveDueLeitner(due);
        return due;
      }
    } catch (e) {
      debugPrint('ApiService.fetchDueLeitner network error (falling back to offline): $e');
    }

    return await OfflineStorageService.loadDueLeitner();
  }

  static Future<Map<String, dynamic>?> fetchStressTest(String ideaId) async {
    try {
      final headers = await _getHeaders();
      final res = await client.get(
        Uri.parse('$baseUrl/api/ai/stress-test/$ideaId'),
        headers: headers,
      ).timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        return jsonDecode(res.body)['stress_test'];
      }
    } catch (e) {
      debugPrint('ApiService.fetchStressTest error: $e');
    }
    return null;
  }

  static Future<bool> submitLeitnerReview(String ideaId, int grade) async {
    try {
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/ideas/$ideaId/leitner-review'),
        headers: headers,
        body: jsonEncode({'grade': grade}),
      ).timeout(const Duration(seconds: 3));
      if (res.statusCode == 200) {
        return true;
      }
    } catch (e) {
      debugPrint('ApiService.submitLeitnerReview network error (queuing offline): $e');
    }

    // Queue offline review to persist user progress on device
    await OfflineStorageService.queueOfflineReview(ideaId, grade);
    return true;
  }

  /// Syncs offline ratings when connection is re-established
  static Future<void> syncPendingReviews() async {
    final pending = await OfflineStorageService.getPendingReviews();
    if (pending.isEmpty) return;

    final headers = await _getHeaders();
    bool allSynced = true;
    for (final review in pending) {
      try {
        final res = await client.post(
          Uri.parse('$baseUrl/api/ideas/${review['idea_id']}/leitner-review'),
          headers: headers,
          body: jsonEncode({'grade': review['grade']}),
        ).timeout(const Duration(seconds: 3));
        if (res.statusCode != 200) allSynced = false;
      } catch (e) {
        debugPrint('ApiService.syncPendingReviews item error: $e');
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
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/ai/auto-fetch-and-generate'),
        headers: headers,
        body: jsonEncode({
          'query': text,
          'topic': 'Mental Models',
          'provider': 'gemini',
        }),
      ).timeout(const Duration(seconds: 15));

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (e) {
      debugPrint('ApiService.deconstructSharedContent error: $e');
    }
    return null;
  }

  static Future<bool> toggleLike(String ideaId) async {
    try {
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/ideas/$ideaId/like'),
        headers: headers,
      );
      return res.statusCode == 200;
    } catch (e) {
      debugPrint('ApiService.toggleLike error: $e');
      return false;
    }
  }

  static Future<bool> toggleSave(String ideaId) async {
    try {
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/ideas/$ideaId/save'),
        headers: headers,
      );
      return res.statusCode == 200;
    } catch (e) {
      debugPrint('ApiService.toggleSave error: $e');
      return false;
    }
  }

  // --- SOCIAL LEARNING & SHARED STASHES ---

  static Future<List<Map<String, dynamic>>> fetchPublicStashes({String? search}) async {
    try {
      final uri = Uri.parse('$baseUrl/api/stashes/public').replace(queryParameters: {
        if (search != null && search.isNotEmpty) 'search': search,
      });
      final headers = await _getHeaders();
      final res = await client.get(uri, headers: headers).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final List list = jsonDecode(res.body);
        return list.map((e) => Map<String, dynamic>.from(e)).toList();
      }
    } catch (e) {
      debugPrint('ApiService.fetchPublicStashes error: $e');
    }
    return [];
  }

  static Future<Map<String, dynamic>?> fetchSharedStash(String shareSlugOrId) async {
    try {
      final headers = await _getHeaders();
      final res = await client.get(
        Uri.parse('$baseUrl/api/stashes/share/$shareSlugOrId'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (e) {
      debugPrint('ApiService.fetchSharedStash error: $e');
    }
    return null;
  }

  static Future<bool> publishStash(String stashId, {bool isPublic = true}) async {
    try {
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/stashes/$stashId/publish'),
        headers: headers,
        body: jsonEncode({'is_public': isPublic}),
      ).timeout(const Duration(seconds: 4));
      return res.statusCode == 200;
    } catch (e) {
      debugPrint('ApiService.publishStash error: $e');
      return false;
    }
  }

  static Future<Map<String, dynamic>?> cloneStash(String stashId) async {
    try {
      final headers = await _getHeaders();
      final res = await client.post(
        Uri.parse('$baseUrl/api/stashes/$stashId/clone'),
        headers: headers,
      ).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      }
    } catch (e) {
      debugPrint('ApiService.cloneStash error: $e');
    }
    return null;
  }
}
