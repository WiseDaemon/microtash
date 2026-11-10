import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/idea.dart';
import '../models/book.dart';

class ApiService {
  // 10.0.2.2 maps to localhost from the Android Emulator; configure your live server domain for release
  static const String baseUrl = 'http://10.0.2.2:8000';

  // In-memory offline cache fallback
  static List<Idea> _cachedIdeas = [];
  static List<Book> _cachedBooks = [];
  static List<Idea> _cachedLeitnerDue = [];

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
          _cachedIdeas = ideas;
        }
        return ideas;
      }
    } catch (_) {
      // Return offline fallback cache if network is unavailable
      if (_cachedIdeas.isNotEmpty) {
        return _cachedIdeas;
      }
    }
    return _cachedIdeas;
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
          _cachedBooks = books;
        }
        return books;
      }
    } catch (_) {
      if (_cachedBooks.isNotEmpty) {
        return _cachedBooks;
      }
    }
    return _cachedBooks;
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
        _cachedLeitnerDue = due;
        return due;
      }
    } catch (_) {
      if (_cachedLeitnerDue.isNotEmpty) {
        return _cachedLeitnerDue;
      }
    }
    return _cachedLeitnerDue;
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
      );
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
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
