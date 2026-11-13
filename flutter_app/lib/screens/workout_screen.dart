import 'package:flutter/material.dart';
import '../models/idea.dart';
import '../services/api_service.dart';
import '../services/notification_service.dart';
import 'stress_test_screen.dart';

class WorkoutScreen extends StatefulWidget {
  const WorkoutScreen({super.key});

  @override
  State<WorkoutScreen> createState() => _WorkoutScreenState();
}

class _WorkoutScreenState extends State<WorkoutScreen> {
  bool _isLoading = true;
  List<Idea> _dueIdeas = [];
  int _currentIndex = 0;
  bool _isFlipped = false;

  @override
  void initState() {
    super.initState();
    _loadDueCards();
  }

  Future<void> _loadDueCards() async {
    setState(() => _isLoading = true);
    final due = await ApiService.fetchDueLeitner();
    if (due.isNotEmpty) {
      NotificationService.checkDueCardsAndNotify(due.length);
    }
    setState(() {
      _dueIdeas = due;
      _isLoading = false;
      _currentIndex = 0;
      _isFlipped = false;
    });
  }

  void _showNotificationDialog() async {
    bool enabled = await NotificationService.isReminderEnabled();
    if (!mounted) return;

    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dCtx, setDState) {
            return Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF10B981).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.notifications_active, color: Color(0xFF10B981), size: 24),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Daily Recall Reminder',
                        style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Receive a gentle daily notification when your Leitner cards become due. Retain concepts in 3 minutes of active recall.',
                    style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.4),
                  ),
                  const SizedBox(height: 20),
                  SwitchListTile(
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Daily Workout Notification (9:00 AM)', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600)),
                    subtitle: Text(enabled ? 'Enabled • Channel: microstash_recall' : 'Disabled', style: TextStyle(color: enabled ? const Color(0xFF10B981) : Colors.white38, fontSize: 12)),
                    value: enabled,
                    activeColor: const Color(0xFF10B981),
                    onChanged: (val) async {
                      await NotificationService.setReminderEnabled(val);
                      setDState(() => enabled = val);
                    },
                  ),
                  const SizedBox(height: 16),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _reviewCard(int grade) async {
    if (_dueIdeas.isEmpty || _currentIndex >= _dueIdeas.length) return;
    final idea = _dueIdeas[_currentIndex];
    await ApiService.submitLeitnerReview(idea.id, grade);

    setState(() {
      _currentIndex++;
      _isFlipped = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Color(0xFF0F172A),
        body: Center(child: CircularProgressIndicator(color: Color(0xFF10B981))),
      );
    }

    if (_dueIdeas.isEmpty || _currentIndex >= _dueIdeas.length) {
      return Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: const Color(0xFF064E3B),
                    shape: BoxShape.circle,
                    border: Border.all(color: const Color(0xFF10B981), width: 2),
                  ),
                  child: const Icon(Icons.check, color: Color(0xFF34D399), size: 40),
                ),
                const SizedBox(height: 20),
                const Text(
                  'Daily Cognitive Workout Complete!',
                  style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 10),
                const Text(
                  'All due mental models have been reinforced for today. Your long-term memory consolidation is active.',
                  style: TextStyle(color: Colors.white70, fontSize: 13, height: 1.5),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Return to Feed'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    final idea = _dueIdeas[_currentIndex];

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: Text(
          'Workout (${_currentIndex + 1}/${_dueIdeas.length})',
          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_active_outlined, color: Color(0xFF10B981), size: 20),
            tooltip: 'Daily Recall Reminders',
            onPressed: _showNotificationDialog,
          ),
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Center(
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF3B82F6).withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF60A5FA).withOpacity(0.4)),
                ),
                child: Text('Box ${idea.leitnerBox}', style: const TextStyle(color: Color(0xFF93C5FD), fontSize: 11, fontWeight: FontWeight.bold)),
              ),
            ),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: GestureDetector(
                onTap: () => setState(() => _isFlipped = !_isFlipped),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 300),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _isFlipped ? const Color(0xFF10B981) : const Color(0xFF334155), width: 1.5),
                    boxShadow: [
                      BoxShadow(color: Colors.black.withOpacity(0.3), blurRadius: 12, offset: const Offset(0, 6)),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(idea.topic.toUpperCase(), style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11, fontWeight: FontWeight.bold)),
                          Text(_isFlipped ? 'BACK (EXPLANATION)' : 'FRONT (PROMPT)', style: const TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const Divider(color: Color(0xFF334155), height: 24),
                      Text(idea.title, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 12),
                      Expanded(
                        child: SingleChildScrollView(
                          child: Text(
                            _isFlipped ? (idea.detailedExplanation ?? idea.summary) : idea.oneLiner,
                            style: TextStyle(
                              color: _isFlipped ? Colors.white : Colors.white70,
                              fontSize: _isFlipped ? 14 : 16,
                              height: 1.5,
                              fontStyle: _isFlipped ? FontStyle.normal : FontStyle.italic,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text('Tap to ${_isFlipped ? "see prompt" : "reveal model"}', style: const TextStyle(color: Colors.white38, fontSize: 11)),
                          TextButton.icon(
                            onPressed: () {
                              Navigator.push(context, MaterialPageRoute(builder: (_) => StressTestScreen(idea: idea)));
                            },
                            icon: const Icon(Icons.bolt, color: Color(0xFFF59E0B), size: 16),
                            label: const Text('Stress-Test', style: TextStyle(color: Color(0xFFF59E0B), fontSize: 12, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Rating Controls
            Row(
              children: [
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _reviewCard(1),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF7F1D1D),
                      foregroundColor: const Color(0xFFFCA5A5),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Column(
                      children: [
                        Text('Forgot', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        Text('Reset to Box 1', style: TextStyle(fontSize: 10, color: Colors.white70)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _reviewCard(3),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF78350F),
                      foregroundColor: const Color(0xFFFDE68A),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Column(
                      children: [
                        Text('Hard', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        Text('Review in 3d', style: TextStyle(fontSize: 10, color: Colors.white70)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () => _reviewCard(5),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF064E3B),
                      foregroundColor: const Color(0xFF6EE7B7),
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: const Column(
                      children: [
                        Text('Mastered', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        Text('Advance Box', style: TextStyle(fontSize: 10, color: Colors.white70)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
