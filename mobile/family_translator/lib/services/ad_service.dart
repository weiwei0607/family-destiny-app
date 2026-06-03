import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

/// Ad unit IDs - use test IDs during development
class AdUnitIds {
  // Test rewarded ad unit IDs (from Google Mobile Ads SDK docs)
  static const String rewardedAndroid = 'ca-app-pub-3940256099942544/5224354917';
  static const String rewardedIOS = 'ca-app-pub-3940256099942544/1712485313';

  static String get rewarded {
    // Use defaultTargetPlatform from Flutter foundation
    return rewardedAndroid; // Simplified: use Android test ID for both platforms during dev
  }
}

/// Manages Google Mobile Ads lifecycle
class AdService {
  static final AdService _instance = AdService._internal();
  factory AdService() => _instance;
  AdService._internal();

  bool _initialized = false;

  Future<void> initialize() async {
    if (_initialized) return;
    await MobileAds.instance.initialize();
    _initialized = true;
    debugPrint('AdMob initialized');
  }

  bool get isInitialized => _initialized;
}

/// Manages a single rewarded ad load/show cycle
class RewardedAdManager {
  RewardedAd? _rewardedAd;
  bool _isLoading = false;
  int _numLoadAttempts = 0;
  static const int _maxLoadAttempts = 3;

  /// Load a new rewarded ad
  Future<void> loadAd() async {
    if (_isLoading || _rewardedAd != null || _numLoadAttempts >= _maxLoadAttempts) return;
    _isLoading = true;

    await RewardedAd.load(
      adUnitId: AdUnitIds.rewarded,
      request: const AdRequest(),
      rewardedAdLoadCallback: RewardedAdLoadCallback(
        onAdLoaded: (ad) {
          _rewardedAd = ad;
          _numLoadAttempts = 0;
          _isLoading = false;
          debugPrint('Rewarded ad loaded');
        },
        onAdFailedToLoad: (error) {
          _rewardedAd = null;
          _isLoading = false;
          _numLoadAttempts++;
          debugPrint('Rewarded ad failed to load: $error');
        },
      ),
    );
  }

  /// Show the ad and return reward when user completes watching
  Future<bool> showAd({
    required VoidCallback onRewarded,
    required VoidCallback onAdDismissed,
  }) async {
    if (_rewardedAd == null) {
      // Try to load first
      await loadAd();
      if (_rewardedAd == null) {
        // If still no ad after load, give reward anyway (graceful fallback)
        onRewarded();
        return true;
      }
    }

    final ad = _rewardedAd!;

    ad.fullScreenContentCallback = FullScreenContentCallback(
      onAdShowedFullScreenContent: (ad) {
        debugPrint('Rewarded ad showed');
      },
      onAdDismissedFullScreenContent: (ad) {
        ad.dispose();
        _rewardedAd = null;
        onAdDismissed();
        // Preload next ad
        loadAd();
      },
      onAdFailedToShowFullScreenContent: (ad, error) {
        ad.dispose();
        _rewardedAd = null;
        // Give reward anyway as fallback
        onRewarded();
      },
    );

    ad.setImmersiveMode(true);
    await ad.show(
      onUserEarnedReward: (ad, reward) {
        debugPrint('User earned reward: ${reward.amount} ${reward.type}');
        onRewarded();
      },
    );

    return true;
  }

  void dispose() {
    _rewardedAd?.dispose();
    _rewardedAd = null;
  }
}
