class Idea {
  final String id;
  final String title;
  final String oneLiner;
  final String summary;
  final String? detailedExplanation;
  final String? example;
  final String? visualDiagram;
  final String? quote;
  final String? actionItem;
  final String author;
  final String source;
  final String? sourceSlug;
  final String publisher;
  final String copyrightNotice;
  final String topic;
  final List<String> tags;
  final int readTimeMins;
  final String colorTheme;
  final int likes;
  final int savedCount;
  final bool isLiked;
  final bool isSaved;
  final int leitnerBox;
  final String? nextReviewDate;

  Idea({
    required this.id,
    required this.title,
    required this.oneLiner,
    required this.summary,
    this.detailedExplanation,
    this.example,
    this.visualDiagram,
    this.quote,
    this.actionItem,
    required this.author,
    required this.source,
    this.sourceSlug,
    this.publisher = 'Original Publication',
    required this.copyrightNotice,
    required this.topic,
    required this.tags,
    this.readTimeMins = 1,
    this.colorTheme = 'indigo',
    this.likes = 0,
    this.savedCount = 0,
    this.isLiked = false,
    this.isSaved = false,
    this.leitnerBox = 1,
    this.nextReviewDate,
  });

  factory Idea.fromJson(Map<String, dynamic> json) {
    final author = json['author'] ?? 'Thinker';
    final source = json['source'] ?? 'Book';
    final publisher = json['publisher'] ?? 'Original Publication';
    final notice = json['copyright_notice'] ??
        'Transformative educational commentary & mental model summary based on "$source" by $author. All original book copyrights belong to the respective author and publisher.';

    return Idea(
      id: json['id']?.toString() ?? '',
      title: json['title'] ?? 'Mental Model',
      oneLiner: json['one_liner'] ?? '',
      summary: json['summary'] ?? '',
      detailedExplanation: json['detailed_explanation'],
      example: json['example'],
      visualDiagram: json['visual_diagram'],
      quote: json['quote'],
      actionItem: json['action_item'],
      author: author,
      source: source,
      sourceSlug: json['source_slug'],
      publisher: publisher,
      copyrightNotice: notice,
      topic: json['topic'] ?? 'Mental Models',
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      readTimeMins: json['read_time_mins'] ?? 1,
      colorTheme: json['color_theme'] ?? 'indigo',
      likes: json['likes'] ?? 0,
      savedCount: json['saved_count'] ?? 0,
      isLiked: (json['is_liked'] == 1 || json['is_liked'] == true),
      isSaved: (json['is_saved'] == 1 || json['is_saved'] == true),
      leitnerBox: json['leitner_box'] ?? 1,
      nextReviewDate: json['next_review_date'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'one_liner': oneLiner,
      'summary': summary,
      'detailed_explanation': detailedExplanation,
      'example': example,
      'visual_diagram': visualDiagram,
      'quote': quote,
      'action_item': actionItem,
      'author': author,
      'source': source,
      'source_slug': sourceSlug,
      'publisher': publisher,
      'copyright_notice': copyrightNotice,
      'topic': topic,
      'tags': tags,
      'read_time_mins': readTimeMins,
      'color_theme': colorTheme,
      'likes': likes,
      'saved_count': savedCount,
      'is_liked': isLiked,
      'is_saved': isSaved,
      'leitner_box': leitnerBox,
      'next_review_date': nextReviewDate,
    };
  }
}
