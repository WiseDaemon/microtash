import 'package:flutter/material.dart';
import '../models/idea.dart';
import '../services/api_service.dart';
import 'stress_test_screen.dart';
import 'workout_screen.dart';

class FeedScreen extends StatefulWidget {
  const FeedScreen({super.key});

  @override
  State<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> {
  List<Idea> _ideas = [];
  bool _isLoading = true;
  String _selectedTopic = 'All';

  final List<String> _topics = [
    'All',
    'Mental Models',
    'Productivity',
    'Stoicism',
    'Wealth',
    'Psychology',
    'Strategy'
  ];

  @override
  void initState() {
    super.initState();
    _loadIdeas();
  }

  Future<void> _loadIdeas() async {
    setState(() => _isLoading = true);
    final data = await ApiService.fetchIdeas(topic: _selectedTopic);
    setState(() {
      _ideas = data;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.psychology, color: Color(0xFF10B981), size: 24),
            SizedBox(width: 8),
            Text(
              'MICROSTASH',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18, letterSpacing: 1.0),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: TextButton.icon(
              onPressed: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const WorkoutScreen()));
              },
              icon: const Icon(Icons.bolt, color: Color(0xFFF59E0B), size: 18),
              label: const Text('Workout', style: TextStyle(color: Color(0xFFF59E0B), fontWeight: FontWeight.bold, fontSize: 13)),
              style: TextButton.styleFrom(
                backgroundColor: const Color(0xFF78350F).withOpacity(0.3),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // Topic Filter Bar
          Container(
            height: 48,
            margin: const EdgeInsets.symmetric(vertical: 8),
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: _topics.length,
              itemBuilder: (context, index) {
                final topic = _topics[index];
                final isSelected = _selectedTopic == topic;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: ChoiceChip(
                    label: Text(topic),
                    selected: isSelected,
                    onSelected: (val) {
                      if (val) {
                        setState(() => _selectedTopic = topic);
                        _loadIdeas();
                      }
                    },
                    selectedColor: const Color(0xFF10B981),
                    backgroundColor: const Color(0xFF1E293B),
                    labelStyle: TextStyle(
                      color: isSelected ? Colors.white : Colors.white70,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    ),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                );
              },
            ),
          ),

          // Cards List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator(color: Color(0xFF10B981)))
                : _ideas.isEmpty
                    ? const Center(child: Text('No mental models found', style: TextStyle(color: Colors.white70)))
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _ideas.length,
                        itemBuilder: (context, index) {
                          final idea = _ideas[index];
                          return Card(
                            color: const Color(0xFF1E293B),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(18),
                              side: const BorderSide(color: Color(0xFF334155), width: 1),
                            ),
                            margin: const EdgeInsets.only(bottom: 16),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(
                                        idea.topic.toUpperCase(),
                                        style: const TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold),
                                      ),
                                      Text('${idea.readTimeMins} min read', style: const TextStyle(color: Colors.white38, fontSize: 11)),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    idea.title,
                                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    idea.oneLiner,
                                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13, height: 1.4),
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    idea.summary,
                                    style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.45),
                                    maxLines: 3,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 14),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Expanded(
                                        child: Text(
                                          '— ${idea.author} • ${idea.source}',
                                          style: const TextStyle(color: Colors.white54, fontSize: 11, fontStyle: FontStyle.italic),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      ElevatedButton.icon(
                                        onPressed: () {
                                          Navigator.push(
                                            context,
                                            MaterialPageRoute(
                                              builder: (_) => StressTestScreen(
                                                idea: idea,
                                              ),
                                            ),
                                          );
                                        },
                                        icon: const Icon(Icons.bolt, size: 16, color: Color(0xFFF59E0B)),
                                        label: const Text('Stress-Test', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: const Color(0xFF78350F).withOpacity(0.3),
                                          foregroundColor: const Color(0xFFF59E0B),
                                          elevation: 0,
                                          shape: RoundedRectangleBorder(
                                            borderRadius: BorderRadius.circular(10),
                                            side: BorderSide(color: const Color(0xFFF59E0B).withOpacity(0.4)),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  // Transformative Fair Use Educational Credit
                                  Text(
                                    idea.copyrightNotice,
                                    style: TextStyle(color: Colors.white.withOpacity(0.35), fontSize: 9, fontStyle: FontStyle.italic),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
