import 'idea.dart';

class Book {
  final String id;
  final String title;
  final String normalizedTitle;
  final String author;
  final String publisher;
  final String copyrightNotice;
  final String? description;
  final String? coverUrl;
  final String topic;
  final int ideasCount;
  final String scannedByUser;
  final String scannedAt;
  final String scanStatus;
  final List<Idea> ideas;
  final String? stashId;

  Book({
    required this.id,
    required this.title,
    required this.normalizedTitle,
    required this.author,
    this.publisher = 'Original Publication',
    required this.copyrightNotice,
    this.description,
    this.coverUrl,
    this.topic = 'Mental Models',
    this.ideasCount = 0,
    this.scannedByUser = 'community',
    required this.scannedAt,
    this.scanStatus = 'completed',
    this.ideas = const [],
    this.stashId,
  });

  factory Book.fromJson(Map<String, dynamic> json) {
    final title = json['title'] ?? 'Book Title';
    final author = json['author'] ?? 'Author';
    final publisher = json['publisher'] ?? 'Original Publication';
    final notice = json['copyright_notice'] ??
        'Transformative educational commentary & mental model summary of "$title" by $author. All original book trademarks, copyrights, and intellectual property remain with the author and publisher.';

    final rawIdeas = json['ideas'] as List<dynamic>?;
    final List<Idea> parsedIdeas = rawIdeas != null
        ? rawIdeas.map((e) => Idea.fromJson(e as Map<String, dynamic>)).toList()
        : [];

    return Book(
      id: json['id']?.toString() ?? '',
      title: title,
      normalizedTitle: json['normalized_title'] ?? '',
      author: author,
      publisher: publisher,
      copyrightNotice: notice,
      description: json['description'],
      coverUrl: json['cover_url'],
      topic: json['topic'] ?? 'Mental Models',
      ideasCount: json['ideas_count'] ?? parsedIdeas.length,
      scannedByUser: json['scanned_by_user'] ?? 'community',
      scannedAt: json['scanned_at'] ?? DateTime.now().toIso8601String(),
      scanStatus: json['scan_status'] ?? 'completed',
      ideas: parsedIdeas,
      stashId: json['stash_id'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'normalized_title': normalizedTitle,
      'author': author,
      'publisher': publisher,
      'copyright_notice': copyrightNotice,
      'description': description,
      'cover_url': coverUrl,
      'topic': topic,
      'ideas_count': ideasCount,
      'scanned_by_user': scannedByUser,
      'scanned_at': scannedAt,
      'scan_status': scanStatus,
      'ideas': ideas.map((e) => e.toJson()).toList(),
      'stash_id': stashId,
    };
  }
}
