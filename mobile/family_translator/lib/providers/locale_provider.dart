import 'package:flutter/material.dart';

class LocaleProvider extends ChangeNotifier {
  Locale _locale = const Locale('zh', 'TW');

  Locale get locale => _locale;

  void setLocale(Locale locale) {
    if (!['zh_TW', 'zh_CN', 'en'].contains(locale.toString().replaceAll('-', '_'))) {
      return;
    }
    _locale = locale;
    notifyListeners();
  }

  String get langCode {
    if (_locale.languageCode == 'zh') {
      if (_locale.countryCode == 'CN') return 'zh-CN';
      return 'zh-TW';
    }
    return _locale.languageCode;
  }

  String get localeName {
    switch (langCode) {
      case 'zh-TW':
        return '繁體中文';
      case 'zh-CN':
        return '简体中文';
      case 'en':
        return 'English';
      default:
        return '繁體中文';
    }
  }
}
