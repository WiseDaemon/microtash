import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/idea.dart';

class ApiService {
  // Point this to your Google Cloud Run / Render domain in production
  static const String baseUrl = 'http://10.0.2.2:8000'; // 10.0.2.2 maps to localhost from Android Emulator

  static Future<List<Idea>> fetchIdeas({String? topic, String? query}) async {
    final uri = Uri.parse('$baseUrl/api/ideas').replace(queryParameters: {
      if (topic != null && topic != 'All' && topic != 'all') 'topic': topic,
      if (query != null && query.isNotEmpty) 'q': query,
    });

    final res = await http.get(uri);
    if (res.statusCode == 200) {
      final List data = jsonDecode(res.body);
      return data.map((e) => Idea.fromJson(e)).toList();
    }
    return [];
  }

  static Future<List<Idea>> fetchDueLeitner() async {
    final res = await http.get(Uri.parse('$baseUrl/api/ideas/leitner/due'));
    if (res.statusCode == 200) {
      final List data = jsonDecode(res.body);
      return data.map((e) => Idea.fromJson(e)).toList();
    }
    return [];
  }

  static Future<Map<String, dynamic>?> fetchStressTest(String ideaId) async {
    final res = await http.get(Uri.parse('$baseUrl/api/ai/stress-test/$ideaId'));
    if (res.statusCode == 200) {
      return jsonDecode(res.body)['stress_test'];
    }
    return null;
  }

  static Future<bool> submitLeitnerReview(String ideaId, int grade) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/ideas/$ideaId/leitner-review'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'grade': grade}),
    );
    return res.statusCode == 200;
  }

  static Future<bool> toggleLike(String ideaId) async {
    final res = await http.post(Uri.parse('$baseUrl/api/ideas/$ideaId/like'));
    return res.statusCode == 200;
  }

  static Future<bool> toggleSave(String ideaId) async {
    final res = await http.post(Uri.parse('$baseUrl/api/ideas/$ideaId/save'));
    return res.statusCode == 200;
  }
}
