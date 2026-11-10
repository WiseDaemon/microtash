import 'package:flutter/material.dart';
import '../models/idea.dart';
import '../services/api_service.dart';

class StressTestScreen extends StatefulWidget {
  final Idea idea;

  const StressTestScreen({super.key, required this.idea});

  @override
  State<StressTestScreen> createState() => _StressTestScreenState();
}

class _StressTestScreenState extends State<StressTestScreen> {
  bool _isLoading = true;
  Map<String, dynamic>? _dilemma;
  Map<String, dynamic>? _selectedOption;

  @override
  void initState() {
    super.initState();
    _loadDilemma();
  }

  Future<void> _loadDilemma() async {
    setState(() {
      _isLoading = true;
      _selectedOption = null;
    });

    final res = await ApiService.fetchStressTest(widget.idea.id);
    setState(() {
      _dilemma = res ?? {
        'scenario': 'Your team is facing critical execution bottlenecks with ambiguous trade-offs. Stakeholders are panicking.',
        'question': 'How do you apply ${widget.idea.title} to make the optimal move?',
        'options': [
          {'id': 'A', 'text': 'React to initial emotional demands immediately.', 'is_correct': false, 'feedback': 'Trap: Superficial reaction violates core constraints.'},
          {'id': 'B', 'text': 'Isolate the core constraint and protect against downside risk.', 'is_correct': true, 'feedback': 'Correct! First-principles mastery.'},
          {'id': 'C', 'text': 'Compromise equally across all opinions.', 'is_correct': false, 'feedback': 'Compromise dilutes leverage.'}
        ],
        'first_principles_takeaway': 'Eliminate single points of failure first, then maximize asymmetric leverage.'
      };
      _isLoading = false;
    });
  }

  void _selectOption(Map<String, dynamic> option) {
    if (_selectedOption != null) return;
    setState(() {
      _selectedOption = option;
    });

    if (option['is_correct'] == true) {
      ApiService.submitLeitnerReview(widget.idea.id, 5);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('SOCRATIC STRESS-TEST', style: TextStyle(color: Color(0xFFF59E0B), fontSize: 10, fontWeight: FontWeight.w900, letterSpacing: 1.2)),
            Text(widget.idea.title, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold), overflow: TextOverflow.ellipsis),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFFF59E0B)),
            onPressed: _loadDilemma,
            tooltip: 'Regenerate Dilemma',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Color(0xFFF59E0B)),
                  SizedBox(height: 16),
                  Text('Synthesizing high-stakes dilemma...', style: TextStyle(color: Colors.white70, fontSize: 13)),
                ],
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Scenario Card
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E293B),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF334155)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.warning_amber_rounded, color: Color(0xFFF59E0B), size: 18),
                            SizedBox(width: 8),
                            Text('High-Stakes Scenario', style: TextStyle(color: Color(0xFFF59E0B), fontWeight: FontWeight.bold, fontSize: 12)),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          _dilemma!['scenario'] ?? '',
                          style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Question
                  Text(
                    _dilemma!['question'] ?? 'What is the optimal move?',
                    style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 12),

                  // Options
                  ...(_dilemma!['options'] as List? ?? []).map((opt) {
                    final isSelected = _selectedOption == opt;
                    final isCorrect = opt['is_correct'] == true;
                    Color borderColor = const Color(0xFF334155);
                    Color bgColor = const Color(0xFF1E293B);

                    if (_selectedOption != null) {
                      if (isCorrect) {
                        borderColor = const Color(0xFF10B981);
                        bgColor = const Color(0xFF064E3B).withOpacity(0.4);
                      } else if (isSelected && !isCorrect) {
                        borderColor = const Color(0xFFEF4444);
                        bgColor = const Color(0xFF7F1D1D).withOpacity(0.4);
                      }
                    }

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 10.0),
                      child: InkWell(
                        onTap: () => _selectOption(opt),
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: bgColor,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: borderColor, width: 1.5),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                width: 26,
                                height: 26,
                                alignment: Alignment.center,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF334155),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(opt['id'] ?? '', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(opt['text'] ?? '', style: const TextStyle(color: Colors.white70, fontSize: 13, height: 1.4)),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),

                  // Diagnostic Feedback Box
                  if (_selectedOption != null) ...[
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: _selectedOption!['is_correct'] == true
                            ? const Color(0xFF064E3B).withOpacity(0.5)
                            : const Color(0xFF7F1D1D).withOpacity(0.5),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(
                          color: _selectedOption!['is_correct'] == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(
                                _selectedOption!['is_correct'] == true ? Icons.check_circle : Icons.error,
                                color: _selectedOption!['is_correct'] == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                                size: 18,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _selectedOption!['is_correct'] == true ? 'Mastery Confirmed' : 'Cognitive Trap Detected',
                                style: TextStyle(
                                  color: _selectedOption!['is_correct'] == true ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 13,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            _selectedOption!['feedback'] ?? '',
                            style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
                          ),
                        ],
                      ),
                    ),
                  ],

                  // Takeaway
                  if (_dilemma!['first_principles_takeaway'] != null) ...[
                    const SizedBox(height: 14),
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F766E).withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF14B8A6).withOpacity(0.4)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('FIRST-PRINCIPLES HEURISTIC', style: TextStyle(color: Color(0xFF2DD4BF), fontSize: 11, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text(
                            _dilemma!['first_principles_takeaway'],
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w500),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
}
