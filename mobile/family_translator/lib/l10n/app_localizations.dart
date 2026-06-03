import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_zh.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('zh'),
    Locale('zh', 'CN'),
    Locale('zh', 'TW'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In zh_TW, this message translates to:
  /// **'Family Translator'**
  String get appTitle;

  /// No description provided for @tagline.
  ///
  /// In zh_TW, this message translates to:
  /// **'輸入生日，拿到自己的使用手冊 + 家庭的溝通指南'**
  String get tagline;

  /// No description provided for @personalMode.
  ///
  /// In zh_TW, this message translates to:
  /// **'🧑 個人模式'**
  String get personalMode;

  /// No description provided for @loveMode.
  ///
  /// In zh_TW, this message translates to:
  /// **'💕 戀愛合盤'**
  String get loveMode;

  /// No description provided for @familyMode.
  ///
  /// In zh_TW, this message translates to:
  /// **'👨‍👩‍👧‍👦 家庭合盤'**
  String get familyMode;

  /// No description provided for @personalModeSubtitle.
  ///
  /// In zh_TW, this message translates to:
  /// **'免費 · 五系統基礎盤'**
  String get personalModeSubtitle;

  /// No description provided for @loveModeSubtitle.
  ///
  /// In zh_TW, this message translates to:
  /// **'免費基礎合盤 · 深度報告付費解鎖'**
  String get loveModeSubtitle;

  /// No description provided for @familyModeSubtitle.
  ///
  /// In zh_TW, this message translates to:
  /// **'付費解鎖 · 組織架構圖 + 溝通指南'**
  String get familyModeSubtitle;

  /// No description provided for @settings.
  ///
  /// In zh_TW, this message translates to:
  /// **'設定'**
  String get settings;

  /// No description provided for @language.
  ///
  /// In zh_TW, this message translates to:
  /// **'語言'**
  String get language;

  /// No description provided for @traditionalChinese.
  ///
  /// In zh_TW, this message translates to:
  /// **'繁體中文'**
  String get traditionalChinese;

  /// No description provided for @simplifiedChinese.
  ///
  /// In zh_TW, this message translates to:
  /// **'簡體中文'**
  String get simplifiedChinese;

  /// No description provided for @english.
  ///
  /// In zh_TW, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @name.
  ///
  /// In zh_TW, this message translates to:
  /// **'姓名（或暱稱）'**
  String get name;

  /// No description provided for @gender.
  ///
  /// In zh_TW, this message translates to:
  /// **'性別'**
  String get gender;

  /// No description provided for @female.
  ///
  /// In zh_TW, this message translates to:
  /// **'女'**
  String get female;

  /// No description provided for @male.
  ///
  /// In zh_TW, this message translates to:
  /// **'男'**
  String get male;

  /// No description provided for @birthDate.
  ///
  /// In zh_TW, this message translates to:
  /// **'出生日期'**
  String get birthDate;

  /// No description provided for @birthTime.
  ///
  /// In zh_TW, this message translates to:
  /// **'出生時間'**
  String get birthTime;

  /// No description provided for @location.
  ///
  /// In zh_TW, this message translates to:
  /// **'出生地點'**
  String get location;

  /// No description provided for @taipei.
  ///
  /// In zh_TW, this message translates to:
  /// **'台北/新北'**
  String get taipei;

  /// No description provided for @taichung.
  ///
  /// In zh_TW, this message translates to:
  /// **'台中'**
  String get taichung;

  /// No description provided for @kaohsiung.
  ///
  /// In zh_TW, this message translates to:
  /// **'高雄'**
  String get kaohsiung;

  /// No description provided for @other.
  ///
  /// In zh_TW, this message translates to:
  /// **'其他'**
  String get other;

  /// No description provided for @generateReport.
  ///
  /// In zh_TW, this message translates to:
  /// **'🔮 生成我的使用手冊'**
  String get generateReport;

  /// No description provided for @startCompatibility.
  ///
  /// In zh_TW, this message translates to:
  /// **'💕 開始合盤分析'**
  String get startCompatibility;

  /// No description provided for @overview.
  ///
  /// In zh_TW, this message translates to:
  /// **'總覽'**
  String get overview;

  /// No description provided for @bazi.
  ///
  /// In zh_TW, this message translates to:
  /// **'八字'**
  String get bazi;

  /// No description provided for @astrology.
  ///
  /// In zh_TW, this message translates to:
  /// **'占星'**
  String get astrology;

  /// No description provided for @ziwei.
  ///
  /// In zh_TW, this message translates to:
  /// **'紫微'**
  String get ziwei;

  /// No description provided for @humanDesign.
  ///
  /// In zh_TW, this message translates to:
  /// **'人類圖'**
  String get humanDesign;

  /// No description provided for @xingxiu.
  ///
  /// In zh_TW, this message translates to:
  /// **'星宿'**
  String get xingxiu;

  /// No description provided for @energyScore.
  ///
  /// In zh_TW, this message translates to:
  /// **'能量指數'**
  String get energyScore;

  /// No description provided for @unlockFullReport.
  ///
  /// In zh_TW, this message translates to:
  /// **'解鎖完整報告'**
  String get unlockFullReport;

  /// No description provided for @aiDeepReport.
  ///
  /// In zh_TW, this message translates to:
  /// **'AI 深度報告'**
  String get aiDeepReport;

  /// No description provided for @integratedProfile.
  ///
  /// In zh_TW, this message translates to:
  /// **'整合畫像'**
  String get integratedProfile;

  /// No description provided for @lifeLessons.
  ///
  /// In zh_TW, this message translates to:
  /// **'人生課題'**
  String get lifeLessons;

  /// No description provided for @prescription.
  ///
  /// In zh_TW, this message translates to:
  /// **'生活處方籤'**
  String get prescription;

  /// No description provided for @strengths.
  ///
  /// In zh_TW, this message translates to:
  /// **'優點'**
  String get strengths;

  /// No description provided for @weaknesses.
  ///
  /// In zh_TW, this message translates to:
  /// **'缺點'**
  String get weaknesses;

  /// No description provided for @compatibilityScore.
  ///
  /// In zh_TW, this message translates to:
  /// **'綜合評分'**
  String get compatibilityScore;

  /// No description provided for @dimensionAnalysis.
  ///
  /// In zh_TW, this message translates to:
  /// **'五維度分析'**
  String get dimensionAnalysis;

  /// No description provided for @relationshipNarrative.
  ///
  /// In zh_TW, this message translates to:
  /// **'關係敘事'**
  String get relationshipNarrative;

  /// No description provided for @conflictPoints.
  ///
  /// In zh_TW, this message translates to:
  /// **'衝突點'**
  String get conflictPoints;

  /// No description provided for @communicationGuide.
  ///
  /// In zh_TW, this message translates to:
  /// **'溝通指南'**
  String get communicationGuide;

  /// No description provided for @unlockDeepReport.
  ///
  /// In zh_TW, this message translates to:
  /// **'解鎖深度報告'**
  String get unlockDeepReport;

  /// No description provided for @premiumRequired.
  ///
  /// In zh_TW, this message translates to:
  /// **'需要付費解鎖'**
  String get premiumRequired;

  /// No description provided for @comingSoon.
  ///
  /// In zh_TW, this message translates to:
  /// **'即將推出'**
  String get comingSoon;

  /// No description provided for @free.
  ///
  /// In zh_TW, this message translates to:
  /// **'免費'**
  String get free;

  /// No description provided for @premium.
  ///
  /// In zh_TW, this message translates to:
  /// **'付費'**
  String get premium;

  /// No description provided for @notFortuneTelling.
  ///
  /// In zh_TW, this message translates to:
  /// **'不是算命，是「自我理解 + 關係翻譯」'**
  String get notFortuneTelling;

  /// No description provided for @annualMode.
  ///
  /// In zh_TW, this message translates to:
  /// **'📅 年度運勢'**
  String get annualMode;

  /// No description provided for @annualModeSubtitle.
  ///
  /// In zh_TW, this message translates to:
  /// **'查看這一年的運勢走向與每月重點'**
  String get annualModeSubtitle;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'zh'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when language+country codes are specified.
  switch (locale.languageCode) {
    case 'zh':
      {
        switch (locale.countryCode) {
          case 'CN':
            return AppLocalizationsZhCn();
          case 'TW':
            return AppLocalizationsZhTw();
        }
        break;
      }
  }

  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'zh':
      return AppLocalizationsZh();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
