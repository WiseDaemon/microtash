import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/feed_screen.dart';
import 'screens/discover_screen.dart';
import 'screens/workout_screen.dart';
import 'services/notification_service.dart';
import 'services/share_receiver_service.dart';
import 'services/api_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
      systemNavigationBarColor: Color(0xFF0F172A),
      systemNavigationBarIconBrightness: Brightness.light,
    ),
  );
  await NotificationService.initialize();
  await NotificationService.scheduleDailyWorkoutReminder();
  runApp(const MicrostashApp());
}

class MicrostashApp extends StatelessWidget {
  const MicrostashApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Microstash — Mental Model Gym',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF10B981),
          secondary: Color(0xFFF59E0B),
          surface: Color(0xFF1E293B),
          background: Color(0xFF0F172A),
        ),
      ),
      home: const MainNavigationShell(),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  const MainNavigationShell({super.key});

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> with WidgetsBindingObserver {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    FeedScreen(),
    DiscoverScreen(),
    WorkoutScreen(),
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkSharedIntent();
    });
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      _checkSharedIntent();
    }
  }

  Future<void> _checkSharedIntent() async {
    final shared = await ShareReceiverService.getInitialSharedText();
    if (shared != null && shared.isNotEmpty && mounted) {
      _showSharedContentDialog(shared);
    }
  }

  void _showSharedContentDialog(String text) {
    bool isProcessing = false;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (dialogCtx, setSheetState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(dialogCtx).viewInsets.bottom + 24,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: Colors.white24,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF10B981).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.share, color: Color(0xFF10B981), size: 18),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'Import from Android Share Sheet',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0F172A),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: Colors.white10),
                    ),
                    child: Text(
                      text,
                      style: const TextStyle(fontSize: 12, color: Colors.white70),
                      maxLines: 4,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  const SizedBox(height: 16),
                  if (isProcessing)
                    const Center(
                      child: Padding(
                        padding: EdgeInsets.symmetric(vertical: 8.0),
                        child: CircularProgressIndicator(color: Color(0xFF10B981)),
                      ),
                    )
                  else
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: () async {
                          setSheetState(() => isProcessing = true);
                          final res = await ApiService.deconstructSharedContent(text);
                          if (dialogCtx.mounted) {
                            Navigator.pop(dialogCtx);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                backgroundColor: const Color(0xFF10B981),
                                content: Text(
                                  res != null
                                      ? '⚡ Deconstructed ${res['count'] ?? 0} models and saved globally!'
                                      : 'Added to your library.',
                                  style: const TextStyle(fontWeight: FontWeight.bold),
                                ),
                              ),
                            );
                          }
                        },
                        icon: const Icon(Icons.bolt, color: Colors.black, size: 18),
                        label: const Text(
                          'Deconstruct into Mental Models',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.black),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10B981),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        ),
                      ),
                    ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() => _currentIndex = index);
        },
        backgroundColor: const Color(0xFF1E293B),
        indicatorColor: const Color(0xFF10B981).withOpacity(0.2),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.explore_outlined),
            selectedIcon: Icon(Icons.explore, color: Color(0xFF10B981)),
            label: 'Gym Feed',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book, color: Color(0xFF10B981)),
            label: 'Discover Books',
          ),
          NavigationDestination(
            icon: Icon(Icons.fitness_center_outlined),
            selectedIcon: Icon(Icons.fitness_center, color: Color(0xFF10B981)),
            label: 'Daily Workout',
          ),
        ],
      ),
    );
  }
}
