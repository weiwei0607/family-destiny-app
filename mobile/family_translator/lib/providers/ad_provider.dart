import 'package:flutter/material.dart';
import '../services/ad_service.dart';

/// Manages ad-unlocked premium access state
class AdProvider extends ChangeNotifier {
  DateTime? _unlockedUntil;
  bool _isShowingAd = false;
  final _adManager = RewardedAdManager();

  /// Whether premium features are currently unlocked (via ad or purchase)
  bool get isPremiumUnlocked => _unlockedUntil != null && DateTime.now().isBefore(_unlockedUntil!);

  /// When the current unlock expires
  DateTime? get unlockedUntil => _unlockedUntil;

  /// Whether an ad is currently being shown
  bool get isShowingAd => _isShowingAd;

  /// Time remaining until unlock expires (formatted string)
  String get timeRemaining {
    if (!isPremiumUnlocked) return '';
    final diff = _unlockedUntil!.difference(DateTime.now());
    if (diff.inHours > 0) {
      return '${diff.inHours}小時${diff.inMinutes % 60}分鐘';
    }
    return '${diff.inMinutes}分鐘';
  }

  /// Initialize and preload ad
  Future<void> initialize() async {
    await AdService().initialize();
    await _adManager.loadAd();
  }

  /// Watch a rewarded ad to unlock premium for a duration
  Future<bool> watchAdToUnlock({
    Duration unlockDuration = const Duration(hours: 1),
  }) async {
    if (_isShowingAd) return false;
    _isShowingAd = true;
    notifyListeners();

    bool rewarded = false;

    await _adManager.showAd(
      onRewarded: () {
        rewarded = true;
        _unlockedUntil = DateTime.now().add(unlockDuration);
      },
      onAdDismissed: () {
        _isShowingAd = false;
        notifyListeners();
      },
    );

    // If ad failed to show, still unlock as fallback (dev mode)
    if (!rewarded) {
      _unlockedUntil = DateTime.now().add(unlockDuration);
      _isShowingAd = false;
      notifyListeners();
    }

    return rewarded;
  }

  /// Manually unlock (for dev bypass or other methods)
  void unlockForDuration(Duration duration) {
    _unlockedUntil = DateTime.now().add(duration);
    notifyListeners();
  }

  /// Check if unlock has expired and clear if so
  void checkExpiry() {
    if (_unlockedUntil != null && DateTime.now().isAfter(_unlockedUntil!)) {
      _unlockedUntil = null;
      notifyListeners();
    }
  }

  @override
  void dispose() {
    _adManager.dispose();
    super.dispose();
  }
}
