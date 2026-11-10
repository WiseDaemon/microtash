import 'package:flutter/services.dart';

class ShareReceiverService {
  static const MethodChannel _channel = MethodChannel('com.microstash.app/share');

  /// Queries native Android layer to check if the app was opened via the Android Share sheet
  static Future<String?> getInitialSharedText() async {
    try {
      final String? text = await _channel.invokeMethod('getSharedText');
      if (text != null && text.trim().isNotEmpty) {
        return text.trim();
      }
    } catch (_) {}
    return null;
  }
}
